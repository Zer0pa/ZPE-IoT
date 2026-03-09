use crate::bitpack::{pack, unpack};
use crate::codec::{decode_into, encode, Config, Mode};
use crate::presets::Preset;
use core::slice;

#[repr(C)]
#[derive(Clone, Copy)]
pub struct zpe_iot_config_t {
    pub mode: u8,
    pub threshold: f64,
    pub step: f64,
    pub bands0: f64,
    pub bands1: f64,
    pub bands2: f64,
    pub adaptive: u8,
    pub thr_min: f64,
    pub thr_max: f64,
    pub alpha: f64,
    pub k: f64,
    pub preset_id: u8,
}

impl From<zpe_iot_config_t> for Config {
    fn from(value: zpe_iot_config_t) -> Self {
        let mode = match value.mode {
            0 => Mode::Fast,
            1 => Mode::Balanced,
            2 => Mode::LosslessDelta,
            _ => Mode::Balanced,
        };
        Config {
            mode,
            threshold: value.threshold,
            step: value.step,
            bands: [value.bands0, value.bands1, value.bands2],
            adaptive: value.adaptive != 0,
            thr_min: value.thr_min,
            thr_max: value.thr_max,
            alpha: value.alpha,
            k: value.k,
            preset_id: value.preset_id,
        }
    }
}

impl From<Config> for zpe_iot_config_t {
    fn from(value: Config) -> Self {
        Self {
            mode: value.mode as u8,
            threshold: value.threshold,
            step: value.step,
            bands0: value.bands[0],
            bands1: value.bands[1],
            bands2: value.bands[2],
            adaptive: value.adaptive as u8,
            thr_min: value.thr_min,
            thr_max: value.thr_max,
            alpha: value.alpha,
            k: value.k,
            preset_id: value.preset_id,
        }
    }
}

#[no_mangle]
/// # Safety
///
/// Callers must provide valid, non-null pointers:
/// - `samples` references `n_samples` contiguous `f64` values.
/// - `config` references one valid `zpe_iot_config_t`.
/// - `out_bytes` references `out_capacity` writable bytes.
pub unsafe extern "C" fn zpe_iot_encode(
    samples: *const f64,
    n_samples: usize,
    config: *const zpe_iot_config_t,
    out_bytes: *mut u8,
    out_capacity: usize,
) -> i32 {
    if samples.is_null() || config.is_null() || out_bytes.is_null() {
        return -1;
    }

    let samples_slice = unsafe { slice::from_raw_parts(samples, n_samples) };
    let cfg = unsafe { *config };

    let stream = match encode::<8192>(samples_slice, &cfg.into()) {
        Ok(v) => v,
        Err(_) => return -2,
    };

    let out_slice = unsafe { slice::from_raw_parts_mut(out_bytes, out_capacity) };
    match pack(&stream, out_slice) {
        Ok(n) => n as i32,
        Err(_) => -3,
    }
}

#[no_mangle]
/// # Safety
///
/// Callers must provide valid, non-null pointers:
/// - `packed` references `packed_len` bytes containing one packed stream.
/// - `out_samples` references `out_capacity` writable `f64` slots.
pub unsafe extern "C" fn zpe_iot_decode(
    packed: *const u8,
    packed_len: usize,
    out_samples: *mut f64,
    out_capacity: usize,
) -> i32 {
    if packed.is_null() || out_samples.is_null() {
        return -1;
    }

    let packed_slice = unsafe { slice::from_raw_parts(packed, packed_len) };
    let stream = match unpack::<8192>(packed_slice) {
        Ok(v) => v,
        Err(_) => return -2,
    };

    let out_slice = unsafe { slice::from_raw_parts_mut(out_samples, out_capacity) };
    match decode_into(&stream, out_slice) {
        Ok(n) => n as i32,
        Err(_) => -3,
    }
}

#[no_mangle]
pub extern "C" fn zpe_iot_compression_ratio(packed_size: usize, sample_count: usize) -> f32 {
    if packed_size == 0 {
        return 0.0;
    }
    ((sample_count * 8) as f32) / (packed_size as f32)
}

fn preset_to_cfg(preset: Preset) -> zpe_iot_config_t {
    preset.config().into()
}

#[no_mangle]
pub extern "C" fn zpe_iot_preset_temperature() -> zpe_iot_config_t {
    preset_to_cfg(Preset::Temperature)
}

#[no_mangle]
pub extern "C" fn zpe_iot_preset_vibration() -> zpe_iot_config_t {
    preset_to_cfg(Preset::Vibration)
}

#[no_mangle]
pub extern "C" fn zpe_iot_preset_accelerometer() -> zpe_iot_config_t {
    preset_to_cfg(Preset::Accelerometer)
}

#[no_mangle]
pub extern "C" fn zpe_iot_preset_pressure() -> zpe_iot_config_t {
    preset_to_cfg(Preset::Pressure)
}

#[no_mangle]
pub extern "C" fn zpe_iot_preset_gps_track() -> zpe_iot_config_t {
    preset_to_cfg(Preset::GpsTrack)
}

#[no_mangle]
pub extern "C" fn zpe_iot_preset_voltage() -> zpe_iot_config_t {
    preset_to_cfg(Preset::Voltage)
}

#[no_mangle]
pub extern "C" fn zpe_iot_preset_current() -> zpe_iot_config_t {
    preset_to_cfg(Preset::Current)
}

#[no_mangle]
pub extern "C" fn zpe_iot_preset_flow() -> zpe_iot_config_t {
    preset_to_cfg(Preset::Flow)
}

#[no_mangle]
pub extern "C" fn zpe_iot_preset_generic() -> zpe_iot_config_t {
    preset_to_cfg(Preset::Generic)
}
