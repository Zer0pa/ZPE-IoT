use heapless::Vec;

use crate::codec::{EncodedStream, Mode};

pub const PACKET_MAGIC: u16 = 0x5A50;
pub const PACKET_MAGIC_ZERO_SPECIAL: u16 = 0x5A51;
pub const PACKET_VERSION: u8 = 0x01;
pub const PACKET_FLAG_COMPACT_RUNS: u8 = 0x01;
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
    CorruptPayload,
}

struct BitWriter {
    scratch: u32,
    scratch_bits: u8,
}

impl BitWriter {
    fn new() -> Self {
        Self { scratch: 0, scratch_bits: 0 }
    }

    fn write_bits(&mut self, output: &mut [u8], idx: &mut usize, value: u16, width: u8) -> Result<(), PackError> {
        let mask = if width == 16 {
            u32::from(u16::MAX)
        } else {
            (1u32 << width) - 1
        };
        self.scratch = (self.scratch << width) | (u32::from(value) & mask);
        self.scratch_bits += width;

        while self.scratch_bits >= 8 {
            self.scratch_bits -= 8;
            if *idx >= output.len() {
                return Err(PackError::OutputTooSmall);
            }
            output[*idx] = ((self.scratch >> self.scratch_bits) & 0xFF) as u8;
            *idx += 1;
            self.scratch = if self.scratch_bits == 0 {
                0
            } else {
                self.scratch & ((1u32 << self.scratch_bits) - 1)
            };
        }
        Ok(())
    }

    fn finish(&mut self, output: &mut [u8], idx: &mut usize) -> Result<(), PackError> {
        if self.scratch_bits > 0 {
            if *idx >= output.len() {
                return Err(PackError::OutputTooSmall);
            }
            output[*idx] = (self.scratch << (8 - self.scratch_bits)) as u8;
            *idx += 1;
            self.scratch = 0;
            self.scratch_bits = 0;
        }
        Ok(())
    }
}

struct BitReader<'a> {
    bytes: &'a [u8],
    bit_pos: usize,
}

impl<'a> BitReader<'a> {
    fn new(bytes: &'a [u8]) -> Self {
        Self { bytes, bit_pos: 0 }
    }

    fn read_bits(&mut self, width: u8) -> Result<u16, UnpackError> {
        if self.bit_pos + width as usize > self.bytes.len() * 8 {
            return Err(UnpackError::CorruptPayload);
        }

        let mut value = 0u16;
        let mut i = 0u8;
        while i < width {
            let byte = self.bytes[self.bit_pos >> 3];
            let shift = 7 - (self.bit_pos & 7);
            value = (value << 1) | (((byte >> shift) & 0x01) as u16);
            self.bit_pos += 1;
            i += 1;
        }
        Ok(value)
    }

    fn padding_is_zero(&self) -> bool {
        let mut pos = self.bit_pos;
        while pos < self.bytes.len() * 8 {
            let byte = self.bytes[pos >> 3];
            let shift = 7 - (pos & 7);
            if ((byte >> shift) & 0x01) != 0 {
                return false;
            }
            pos += 1;
        }
        true
    }
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

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum BalancedPacking {
    StandardCompact,
    ZeroSpecialCompact,
}

#[inline]
fn standard_compact_payload_bits(count: u16) -> usize {
    let mut remaining = count;
    let mut bits = 0usize;
    while remaining > 0 {
        let chunk = remaining.min(127);
        bits += if chunk == 1 { 10 } else { 17 };
        remaining -= chunk;
    }
    bits
}

#[inline]
fn zero_special_payload_bits(d: u8, m: u8, count: u16) -> usize {
    let mut remaining = count;
    let mut bits = 0usize;
    while remaining > 0 {
        let chunk = remaining.min(127);
        bits += if d == 0 && m == 0 {
            if chunk == 1 { 2 } else { 9 }
        } else if chunk == 1 {
            11
        } else {
            18
        };
        remaining -= chunk;
    }
    bits
}

fn choose_balanced_packing<const N: usize>(stream: &EncodedStream<N>) -> BalancedPacking {
    let mut standard_bits = 0usize;
    let mut zero_special_bits = 0usize;

    for &(d, m, count) in stream.rle_tokens.iter() {
        standard_bits += standard_compact_payload_bits(count);
        zero_special_bits += zero_special_payload_bits(d, m, count);
    }

    if zero_special_bits < standard_bits {
        BalancedPacking::ZeroSpecialCompact
    } else {
        BalancedPacking::StandardCompact
    }
}

fn pack_standard_compact<const N: usize>(
    stream: &EncodedStream<N>,
    output: &mut [u8],
    idx: &mut usize,
) -> Result<(), PackError> {
    let mut writer = BitWriter::new();
    for &(d, m, count) in stream.rle_tokens.iter() {
        let mut remaining = count;
        while remaining > 0 {
            let chunk = remaining.min(127);
            if chunk == 1 {
                writer.write_bits(output, idx, 0, 1)?;
                writer.write_bits(output, idx, d as u16 & 0x07, 3)?;
                writer.write_bits(output, idx, m as u16 & 0x3F, 6)?;
            } else {
                writer.write_bits(output, idx, 1, 1)?;
                writer.write_bits(output, idx, d as u16 & 0x07, 3)?;
                writer.write_bits(output, idx, m as u16 & 0x3F, 6)?;
                writer.write_bits(output, idx, chunk & 0x7F, 7)?;
            }
            remaining -= chunk;
        }
    }
    writer.finish(output, idx)?;
    Ok(())
}

fn pack_zero_special_compact<const N: usize>(
    stream: &EncodedStream<N>,
    output: &mut [u8],
    idx: &mut usize,
) -> Result<(), PackError> {
    let mut writer = BitWriter::new();
    for &(d, m, count) in stream.rle_tokens.iter() {
        let mut remaining = count;
        while remaining > 0 {
            let chunk = remaining.min(127);
            if d == 0 && m == 0 {
                writer.write_bits(output, idx, 0, 1)?;
                if chunk == 1 {
                    writer.write_bits(output, idx, 0, 1)?;
                } else {
                    writer.write_bits(output, idx, 1, 1)?;
                    writer.write_bits(output, idx, chunk - 2, 7)?;
                }
            } else if chunk == 1 {
                writer.write_bits(output, idx, 1, 1)?;
                writer.write_bits(output, idx, 0, 1)?;
                writer.write_bits(output, idx, d as u16 & 0x07, 3)?;
                writer.write_bits(output, idx, m as u16 & 0x3F, 6)?;
            } else {
                writer.write_bits(output, idx, 1, 1)?;
                writer.write_bits(output, idx, 1, 1)?;
                writer.write_bits(output, idx, d as u16 & 0x07, 3)?;
                writer.write_bits(output, idx, m as u16 & 0x3F, 6)?;
                writer.write_bits(output, idx, chunk & 0x7F, 7)?;
            }
            remaining -= chunk;
        }
    }
    writer.finish(output, idx)?;
    Ok(())
}

pub fn pack<const N: usize>(stream: &EncodedStream<N>, output: &mut [u8]) -> Result<usize, PackError> {
    if stream.sample_count == 0 {
        return Err(PackError::InvalidStream);
    }

    let mut idx = 0usize;
    if output.len() < 14 {
        return Err(PackError::OutputTooSmall);
    }

    let balanced_packing = if matches!(stream.mode, Mode::Balanced | Mode::LosslessDelta) {
        choose_balanced_packing(stream)
    } else {
        BalancedPacking::StandardCompact
    };
    let magic_value = if balanced_packing == BalancedPacking::ZeroSpecialCompact {
        PACKET_MAGIC_ZERO_SPECIAL
    } else {
        PACKET_MAGIC
    };
    let magic = magic_value.to_le_bytes();
    output[idx..idx + 2].copy_from_slice(&magic);
    idx += 2;
    output[idx] = PACKET_VERSION;
    idx += 1;

    let mode_bits = stream.mode as u8;
    let mut flags = (mode_bits << 6) | ((stream.preset_id & 0x0F) << 2) | ((stream.adaptive as u8) << 1);
    if matches!(stream.mode, Mode::Balanced | Mode::LosslessDelta) {
        flags |= PACKET_FLAG_COMPACT_RUNS;
    }
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
            match balanced_packing {
                BalancedPacking::StandardCompact => {
                    pack_standard_compact(stream, output, &mut idx)?;
                }
                BalancedPacking::ZeroSpecialCompact => {
                    pack_zero_special_compact(stream, output, &mut idx)?;
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
    let zero_special = match magic {
        PACKET_MAGIC => false,
        PACKET_MAGIC_ZERO_SPECIAL => true,
        _ => return Err(UnpackError::BadMagic),
    };
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
    let compact = (flags & PACKET_FLAG_COMPACT_RUNS) == PACKET_FLAG_COMPACT_RUNS;

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
            if compact {
                let mut reader = BitReader::new(&bytes[idx..payload_end]);
                let target = sample_count.saturating_sub(1);
                let mut emitted = 0u16;
                while emitted < target {
                    let (d, m, count) = if zero_special {
                        let family = reader.read_bits(1)?;
                        let subtype = reader.read_bits(1)?;
                        if family == 0 {
                            if subtype == 0 {
                                (0u8, 0u8, 1u16)
                            } else {
                                let encoded = reader.read_bits(7)?;
                                (0u8, 0u8, encoded + 2)
                            }
                        } else if subtype == 0 {
                            let d = reader.read_bits(3)? as u8;
                            let m = reader.read_bits(6)? as u8;
                            (d, m, 1u16)
                        } else {
                            let d = reader.read_bits(3)? as u8;
                            let m = reader.read_bits(6)? as u8;
                            let count = reader.read_bits(7)?;
                            if count == 0 {
                                return Err(UnpackError::CorruptPayload);
                            }
                            (d, m, count)
                        }
                    } else {
                        let prefix = reader.read_bits(1)?;
                        let d = reader.read_bits(3)? as u8;
                        let m = reader.read_bits(6)? as u8;
                        let count = if prefix == 0 {
                            1
                        } else {
                            let count = reader.read_bits(7)?;
                            if count == 0 {
                                return Err(UnpackError::CorruptPayload);
                            }
                            count
                        };
                        (d, m, count)
                    };

                    emitted = emitted.checked_add(count).ok_or(UnpackError::CorruptPayload)?;
                    if emitted > target {
                        return Err(UnpackError::CorruptPayload);
                    }
                    rle_tokens.push((d, m, count)).map_err(|_| UnpackError::Capacity)?;
                }
                if !reader.padding_is_zero() {
                    return Err(UnpackError::CorruptPayload);
                }
            } else {
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
                if idx != payload_end {
                    return Err(UnpackError::CorruptPayload);
                }
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

    use super::{pack, unpack, PACKET_MAGIC_ZERO_SPECIAL};

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

    #[test]
    fn compact_balanced_round_trip_handles_count_one_runs() {
        let mut tokens: Vec<(u8, u8, u16), 16> = Vec::new();
        tokens.push((1, 3, 1)).unwrap();
        tokens.push((7, 2, 4)).unwrap();
        tokens.push((0, 0, 1)).unwrap();

        let stream = EncodedStream {
            rle_tokens: tokens,
            start_value: 0.5,
            step: 0.01,
            mode: Mode::Balanced,
            sample_count: 7,
            adaptive: true,
            preset_id: 4,
            metadata: 0,
        };

        let mut out = [0u8; 256];
        let n = pack(&stream, &mut out).unwrap();
        let decoded = unpack::<16>(&out[..n]).unwrap();
        assert_eq!(decoded.rle_tokens, stream.rle_tokens);
    }

    #[test]
    fn zero_special_balanced_round_trip_handles_zero_runs() {
        let mut tokens: Vec<(u8, u8, u16), 16> = Vec::new();
        tokens.push((0, 0, 1)).unwrap();
        tokens.push((0, 0, 4)).unwrap();
        tokens.push((7, 5, 1)).unwrap();
        tokens.push((1, 5, 3)).unwrap();

        let stream = EncodedStream {
            rle_tokens: tokens,
            start_value: 0.25,
            step: 0.01,
            mode: Mode::Balanced,
            sample_count: 10,
            adaptive: true,
            preset_id: 3,
            metadata: 0,
        };

        let mut out = [0u8; 256];
        let n = pack(&stream, &mut out).unwrap();
        let magic = u16::from_le_bytes([out[0], out[1]]);
        assert_eq!(magic, PACKET_MAGIC_ZERO_SPECIAL);

        let decoded = unpack::<16>(&out[..n]).unwrap();
        assert_eq!(decoded.rle_tokens, stream.rle_tokens);
    }
}
