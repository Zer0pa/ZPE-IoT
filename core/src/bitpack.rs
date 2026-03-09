use heapless::Vec;

use crate::codec::{EncodedStream, Mode};

pub const PACKET_MAGIC: u16 = 0x5A50;
pub const PACKET_VERSION: u8 = 0x01;
pub const CRC_POLY: u16 = 0x1021;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PackError {
    OutputTooSmall,
    InvalidStream,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum UnpackError {
    TooShort,
    BadMagic,
    BadVersion,
    BadCrc,
    Capacity,
    InvalidMode,
}

#[inline]
fn crc16_ccitt(data: &[u8]) -> u16 {
    let mut crc: u16 = 0xFFFF;
    for &b in data {
        crc ^= (b as u16) << 8;
        let mut i = 0;
        while i < 8 {
            crc = if (crc & 0x8000) != 0 {
                (crc << 1) ^ CRC_POLY
            } else {
                crc << 1
            };
            i += 1;
        }
    }
    crc
}

#[inline]
fn step_to_fixed(step: f64) -> u16 {
    let scaled = libm::round(step * 10_000.0);
    if scaled <= 0.0 {
        1
    } else if scaled >= u16::MAX as f64 {
        u16::MAX
    } else {
        scaled as u16
    }
}

#[inline]
fn fixed_to_step(value: u16) -> f64 {
    (value as f64) / 10_000.0
}

pub fn pack<const N: usize>(stream: &EncodedStream<N>, output: &mut [u8]) -> Result<usize, PackError> {
    if stream.sample_count == 0 {
        return Err(PackError::InvalidStream);
    }

    let mut idx = 0usize;
    if output.len() < 14 {
        return Err(PackError::OutputTooSmall);
    }

    let magic = PACKET_MAGIC.to_le_bytes();
    output[idx..idx + 2].copy_from_slice(&magic);
    idx += 2;
    output[idx] = PACKET_VERSION;
    idx += 1;

    let mode_bits = stream.mode as u8;
    let flags = (mode_bits << 6) | ((stream.preset_id & 0x0F) << 2) | ((stream.adaptive as u8) << 1);
    output[idx] = flags;
    idx += 1;

    output[idx..idx + 2].copy_from_slice(&stream.sample_count.to_le_bytes());
    idx += 2;
    output[idx..idx + 4].copy_from_slice(&(stream.start_value as f32).to_le_bytes());
    idx += 4;
    output[idx..idx + 2].copy_from_slice(&step_to_fixed(stream.step).to_le_bytes());
    idx += 2;

    match stream.mode {
        Mode::Fast => {
            for &(d, _m, count) in stream.rle_tokens.iter() {
                let mut remaining = count;
                while remaining > 0 {
                    if idx + 1 + 2 > output.len() {
                        return Err(PackError::OutputTooSmall);
                    }
                    let chunk = remaining.min(31);
                    output[idx] = ((d & 0x07) << 5) | ((chunk as u8) & 0x1F);
                    idx += 1;
                    remaining -= chunk;
                }
            }
        }
        Mode::Balanced | Mode::LosslessDelta => {
            for &(d, m, count) in stream.rle_tokens.iter() {
                let mut remaining = count;
                while remaining > 0 {
                    if idx + 2 + 2 > output.len() {
                        return Err(PackError::OutputTooSmall);
                    }
                    let chunk = remaining.min(127);
                    let token: u16 = ((d as u16 & 0x07) << 13)
                        | ((m as u16 & 0x3F) << 7)
                        | (chunk & 0x7F);
                    output[idx..idx + 2].copy_from_slice(&token.to_be_bytes());
                    idx += 2;
                    remaining -= chunk;
                }
            }
        }
    }

    let crc = crc16_ccitt(&output[..idx]).to_le_bytes();
    if idx + 2 > output.len() {
        return Err(PackError::OutputTooSmall);
    }
    output[idx..idx + 2].copy_from_slice(&crc);
    idx += 2;

    Ok(idx)
}

pub fn unpack<const N: usize>(bytes: &[u8]) -> Result<EncodedStream<N>, UnpackError> {
    if bytes.len() < 14 {
        return Err(UnpackError::TooShort);
    }

    let magic = u16::from_le_bytes([bytes[0], bytes[1]]);
    if magic != PACKET_MAGIC {
        return Err(UnpackError::BadMagic);
    }
    if bytes[2] != PACKET_VERSION {
        return Err(UnpackError::BadVersion);
    }

    let payload_end = bytes.len() - 2;
    let expected_crc = u16::from_le_bytes([bytes[payload_end], bytes[payload_end + 1]]);
    let actual_crc = crc16_ccitt(&bytes[..payload_end]);
    if expected_crc != actual_crc {
        return Err(UnpackError::BadCrc);
    }

    let flags = bytes[3];
    let mode = match (flags >> 6) & 0x03 {
        0 => Mode::Fast,
        1 => Mode::Balanced,
        2 => Mode::LosslessDelta,
        _ => return Err(UnpackError::InvalidMode),
    };
    let preset_id = (flags >> 2) & 0x0F;
    let adaptive = ((flags >> 1) & 0x01) != 0;

    let sample_count = u16::from_le_bytes([bytes[4], bytes[5]]);
    let start_value = f32::from_le_bytes([bytes[6], bytes[7], bytes[8], bytes[9]]) as f64;
    let step_fixed = u16::from_le_bytes([bytes[10], bytes[11]]);
    let step = fixed_to_step(step_fixed);

    let mut rle_tokens: Vec<(u8, u8, u16), N> = Vec::new();
    let mut idx = 12usize;

    match mode {
        Mode::Fast => {
            while idx < payload_end {
                let b = bytes[idx];
                idx += 1;
                let d = (b >> 5) & 0x07;
                let count = (b & 0x1F) as u16;
                if count == 0 {
                    continue;
                }
                rle_tokens.push((d, 0, count)).map_err(|_| UnpackError::Capacity)?;
            }
        }
        Mode::Balanced | Mode::LosslessDelta => {
            while idx + 1 < payload_end {
                let token = u16::from_be_bytes([bytes[idx], bytes[idx + 1]]);
                idx += 2;
                let d = ((token >> 13) & 0x07) as u8;
                let m = ((token >> 7) & 0x3F) as u8;
                let count = token & 0x7F;
                if count == 0 {
                    continue;
                }
                rle_tokens.push((d, m, count)).map_err(|_| UnpackError::Capacity)?;
            }
        }
    }

    Ok(EncodedStream {
        rle_tokens,
        start_value,
        step,
        mode,
        sample_count,
        adaptive,
        preset_id,
        metadata: 0,
    })
}

#[cfg(test)]
mod tests {
    use heapless::Vec;

    use crate::codec::{EncodedStream, Mode};

    use super::{pack, unpack};

    #[test]
    fn round_trip_pack_unpack() {
        let mut tokens: Vec<(u8, u8, u16), 16> = Vec::new();
        tokens.push((1, 3, 10)).unwrap();
        tokens.push((7, 2, 5)).unwrap();

        let stream = EncodedStream {
            rle_tokens: tokens,
            start_value: 1.25,
            step: 0.01,
            mode: Mode::Balanced,
            sample_count: 16,
            adaptive: true,
            preset_id: 2,
            metadata: 0,
        };

        let mut out = [0u8; 256];
        let n = pack(&stream, &mut out).unwrap();
        let decoded = unpack::<16>(&out[..n]).unwrap();
        assert_eq!(decoded.sample_count, stream.sample_count);
        assert_eq!(decoded.mode as u8, stream.mode as u8);
        assert_eq!(decoded.rle_tokens.len(), stream.rle_tokens.len());
    }
}
