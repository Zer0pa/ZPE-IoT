use numpy::{IntoPyArray, PyArray1, PyReadonlyArray1};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};

use zpe_iot::{decode_into, encode, pack, unpack, Config, Mode};

fn build_config(
    mode: u8,
    threshold: f64,
    step: f64,
    bands: (f64, f64, f64),
    adaptive: bool,
    thr_min: f64,
    thr_max: f64,
    alpha: f64,
    k: f64,
    preset_id: u8,
) -> Config {
    let resolved_mode = match mode {
        0 => Mode::Fast,
        1 => Mode::Balanced,
        2 => Mode::LosslessDelta,
        _ => Mode::Balanced,
    };

    Config {
        mode: resolved_mode,
        threshold,
        step,
        bands: [bands.0, bands.1, bands.2],
        adaptive,
        thr_min,
        thr_max,
        alpha,
        k,
        preset_id,
    }
}

#[pyfunction]
#[pyo3(
    signature = (
        samples,
        *,
        mode,
        threshold,
        step,
        bands,
        adaptive,
        thr_min,
        thr_max,
        alpha,
        k,
        preset_id
    )
)]
fn encode_packet<'py>(
    py: Python<'py>,
    samples: PyReadonlyArray1<'py, f64>,
    mode: u8,
    threshold: f64,
    step: f64,
    bands: (f64, f64, f64),
    adaptive: bool,
    thr_min: f64,
    thr_max: f64,
    alpha: f64,
    k: f64,
    preset_id: u8,
) -> PyResult<Bound<'py, PyBytes>> {
    let sample_slice = samples
        .as_slice()
        .map_err(|_| PyValueError::new_err("samples must be a contiguous float64 array"))?;

    let config = build_config(mode, threshold, step, bands, adaptive, thr_min, thr_max, alpha, k, preset_id);
    let stream = encode::<8192>(sample_slice, &config)
        .map_err(|_| PyRuntimeError::new_err("native encode failed"))?;

    let mut output = vec![0u8; sample_slice.len().saturating_mul(4).max(256)];
    let packed_len = pack(&stream, &mut output).map_err(|_| PyRuntimeError::new_err("native pack failed"))?;
    Ok(PyBytes::new(py, &output[..packed_len]))
}

#[pyfunction]
fn decode_packet<'py>(py: Python<'py>, packet: &[u8]) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let stream = unpack::<8192>(packet).map_err(|_| PyRuntimeError::new_err("native unpack failed"))?;
    let mut output = vec![0.0f64; stream.sample_count as usize];
    let written = decode_into(&stream, &mut output).map_err(|_| PyRuntimeError::new_err("native decode failed"))?;
    output.truncate(written);
    Ok(output.into_pyarray(py))
}

#[pyfunction]
fn backend_info(py: Python<'_>) -> PyResult<Py<PyDict>> {
    let info = PyDict::new(py);
    info.set_item("backend", "rust")?;
    info.set_item("origin", "pyo3_native_extension")?;
    info.set_item("native", true)?;
    info.set_item("fallback_used", false)?;
    info.set_item("module_name", "zpe_iot._zpe_iot_native")?;
    info.set_item("compiled_extension", true)?;
    Ok(info.unbind())
}

#[pymodule]
fn _zpe_iot_native(_py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(encode_packet, module)?)?;
    module.add_function(wrap_pyfunction!(decode_packet, module)?)?;
    module.add_function(wrap_pyfunction!(backend_info, module)?)?;
    Ok(())
}
