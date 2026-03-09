use heapless::Vec;

use crate::adaptive::{compute_threshold, update_envelope};
use crate::magnitude::{find_magnitude, magnitude_value};
use crate::quantise::{direction_sign, DefaultQuantiser, Quantiser, DIRECTION_DELTAS};

pub const ADAPTIVE_K: f64 = 0.15;
pub const ADAPTIVE_THR_MIN: f64 = 0.001;
pub const ADAPTIVE_THR_MAX: f64 = 1.0;
pub const ADAPTIVE_ALPHA: f64 = 0.95;

#[derive(Clone, Copy, PartialEq, Debug)]
#[repr(u8)]
pub enum Mode {
    Fast = 0,
    Balanced = 1,
    LosslessDelta = 2,
}

#[derive(Clone, Copy, Debug)]
pub struct Config {
    pub mode: Mode,
    pub threshold: f64,
    pub step: f64,
    pub bands: [f64; 3],
    pub adaptive: bool,
    pub thr_min: f64,
    pub thr_max: f64,
    pub alpha: f64,
    pub k: f64,
    pub preset_id: u8,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            mode: Mode::Balanced,
            threshold: 0.05,
            step: 0.0,
            bands: [1.0, 4.0, 16.0],
            adaptive: true,
            thr_min: ADAPTIVE_THR_MIN,
            thr_max: ADAPTIVE_THR_MAX,
            alpha: ADAPTIVE_ALPHA,
            k: ADAPTIVE_K,
            preset_id: 0,
        }
    }
}

#[derive(Clone, Debug)]
pub struct EncodedStream<const N: usize> {
    pub rle_tokens: Vec<(u8, u8, u16), N>,
    pub start_value: f64,
    pub step: f64,
    pub mode: Mode,
    pub sample_count: u16,
    pub adaptive: bool,
    pub preset_id: u8,
    pub metadata: u8,
}

impl<const N: usize> EncodedStream<N> {
    pub fn compression_ratio(&self) -> f64 {
        if self.sample_count == 0 {
            return 0.0;
        }
        let raw_bytes = (self.sample_count as usize) * 8;
        let payload_bytes = match self.mode {
            Mode::Fast => self.rle_tokens.len(),
            Mode::Balanced | Mode::LosslessDelta => self.rle_tokens.len() * 2,
        };
        let packed = 14 + payload_bytes;
        raw_bytes as f64 / packed.max(1) as f64
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CodecError {
    EmptyInput,
    TooManySamples,
    Capacity,
    InvalidOutput,
}

#[inline]
fn compute_auto_step(samples: &[f64]) -> f64 {
    if samples.len() < 2 {
        return 0.001;
    }
    let mut mean = 0.0;
    for &v in samples {
        mean += v;
    }
    mean /= samples.len() as f64;

    let mut var = 0.0;
    for &v in samples {
        let d = v - mean;
        var += d * d;
    }
    var /= samples.len() as f64;

    let std = libm::sqrt(var);
    if std <= 0.0 { 0.001 } else { std / 64.0 }
}

pub fn encode<const N: usize>(samples: &[f64], config: &Config) -> Result<EncodedStream<N>, CodecError> {
    if samples.is_empty() {
        return Err(CodecError::EmptyInput);
    }
    if samples.len() > u16::MAX as usize {
        return Err(CodecError::TooManySamples);
    }
    if samples.len() == 1 {
        return Ok(EncodedStream {
            rle_tokens: Vec::new(),
            start_value: samples[0],
            step: if config.step <= 0.0 { 0.001 } else { config.step },
            mode: config.mode,
            sample_count: 1,
            adaptive: config.adaptive,
            preset_id: config.preset_id,
            metadata: 0,
        });
    }

    let mut threshold = if config.threshold <= 0.0 {
        config.thr_min
    } else {
        config.threshold
    };
    let step = if config.step <= 0.0 {
        compute_auto_step(samples)
    } else {
        config.step
    };

    let quantiser = DefaultQuantiser { bands: config.bands };

    let mut rle_tokens = Vec::<(u8, u8, u16), N>::new();
    let mut reconstructed = samples[0];
    let mut envelope = threshold / config.k.max(1e-9);

    let mut curr_d = 0u8;
    let mut curr_m = 0u8;
    let mut curr_count = 0u16;

    for &sample in &samples[1..] {
        let delta = sample - reconstructed;

        if config.adaptive {
            envelope = update_envelope(envelope, delta.abs(), config.alpha);
            threshold = compute_threshold(envelope, config.k, config.thr_min, config.thr_max);
        }

        let d = quantiser.quantise(delta, threshold);

        let (m_idx, reconstructed_delta) = match config.mode {
            Mode::Fast => (0u8, DIRECTION_DELTAS[d as usize] * step),
            Mode::Balanced | Mode::LosslessDelta => {
                if d == 0 {
                    (0u8, 0.0)
                } else {
                    let idx = find_magnitude(delta.abs(), step);
                    let mag = magnitude_value(idx);
                    (idx, direction_sign(d) * mag * step)
                }
            }
        };

        if curr_count > 0 && d == curr_d && m_idx == curr_m && curr_count < u16::MAX {
            curr_count += 1;
        } else {
            if curr_count > 0 {
                rle_tokens
                    .push((curr_d, curr_m, curr_count))
                    .map_err(|_| CodecError::Capacity)?;
            }
            curr_d = d;
            curr_m = m_idx;
            curr_count = 1;
        }

        reconstructed += reconstructed_delta;
    }

    if curr_count > 0 {
        rle_tokens
            .push((curr_d, curr_m, curr_count))
            .map_err(|_| CodecError::Capacity)?;
    }

    Ok(EncodedStream {
        rle_tokens,
        start_value: samples[0],
        step,
        mode: config.mode,
        sample_count: samples.len() as u16,
        adaptive: config.adaptive,
        preset_id: config.preset_id,
        metadata: 0,
    })
}

pub fn decode_into<const N: usize>(stream: &EncodedStream<N>, output: &mut [f64]) -> Result<usize, CodecError> {
    if output.is_empty() {
        return Err(CodecError::InvalidOutput);
    }

    let target = (stream.sample_count as usize).min(output.len());
    if target == 0 {
        return Ok(0);
    }

    output[0] = stream.start_value;
    let mut idx = 1usize;
    let mut value = stream.start_value;

    match stream.mode {
        Mode::Fast => {
            for &(d, _m_idx, count) in stream.rle_tokens.iter() {
                let delta = DIRECTION_DELTAS[d as usize] * stream.step;
                let mut i = 0u16;
                while i < count {
                    if idx >= target {
                        return Ok(idx);
                    }
                    value += delta;
                    output[idx] = value;
                    idx += 1;
                    i += 1;
                }
            }
        }
        Mode::Balanced | Mode::LosslessDelta => {
            for &(d, m_idx, count) in stream.rle_tokens.iter() {
                let delta = if d == 0 {
                    0.0
                } else {
                    direction_sign(d) * magnitude_value(m_idx) * stream.step
                };
                let mut i = 0u16;
                while i < count {
                    if idx >= target {
                        return Ok(idx);
                    }
                    value += delta;
                    output[idx] = value;
                    idx += 1;
                    i += 1;
                }
            }
        }
    }

    Ok(idx)
}
