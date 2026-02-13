# ZPE-IoT API Reference

## Python API

### `encode(samples, config=None, preset=None, **kwargs) -> EncodedStream`
Parameters: `samples` (1D float sequence), optional `config` or `preset`, optional overrides (`mode`, `threshold`, `step`, `bands`, `adaptive`).
Returns: `EncodedStream`.
Errors: raises `EncodeError` on invalid input.

Example:
```python
import zpe_iot
stream = zpe_iot.encode(samples, preset="vibration")
```

### `decode(stream_or_bytes) -> np.ndarray`
Parameters: `EncodedStream` or packed bytes.
Returns: reconstructed `np.ndarray`.
Errors: raises `ValueError` for invalid packet bytes.

### `Config`
Fields: `mode`, `threshold`, `step`, `bands`, `adaptive`, `thr_min`, `thr_max`, `alpha`, `k`, `preset_id`.

### `Mode`
Values: `fast`, `balanced`, `lossless_delta`.

### `Preset`
Values: `temperature`, `vibration`, `accelerometer`, `pressure`, `gps_track`, `voltage`, `current`, `flow`, `generic`.

### `EncodedStream`
Fields: `rle_tokens`, `start_value`, `step`, `mode`, `sample_count`, `adaptive`, `preset_id`.
Methods: `to_bytes()`, `from_bytes()`, `nrmse(original)`.
Properties: `packed_size`, `compression_ratio`.

### Metrics
- `compute_nrmse(original, reconstructed) -> float`
- `compute_cr(stream, original_samples) -> float`

## Rust API

### `encode<const N: usize>(samples: &[f64], config: &Config) -> Result<EncodedStream<N>, CodecError>`

### `decode_into<const N: usize>(stream: &EncodedStream<N>, output: &mut [f64]) -> Result<usize, CodecError>`

### `Config`
Fields: `mode`, `threshold`, `step`, `bands`, `adaptive`, `thr_min`, `thr_max`, `alpha`, `k`, `preset_id`.

### `Mode`
Variants: `Fast`, `Balanced`, `LosslessDelta`.

### `Preset`
Variants: `Temperature`, `Vibration`, `Accelerometer`, `Pressure`, `GpsTrack`, `Voltage`, `Current`, `Flow`, `Generic`.

### `EncodedStream<N>`
Fields: `rle_tokens`, `start_value`, `step`, `mode`, `sample_count`, `adaptive`, `preset_id`, `metadata`.
Method: `compression_ratio()`.

## C API

### `int32_t zpe_iot_encode(const double* samples, size_t n_samples, const zpe_iot_config_t* config, uint8_t* out_bytes, size_t out_capacity)`
Returns packed byte length on success; negative error code on failure.

### `int32_t zpe_iot_decode(const uint8_t* packed, size_t packed_len, double* out_samples, size_t out_capacity)`
Returns decoded sample count on success; negative error code on failure.

### `float zpe_iot_compression_ratio(size_t packed_size, size_t sample_count)`
Computes CR using raw float64 baseline.

### `zpe_iot_preset_*()`
Returns predefined `zpe_iot_config_t` for each sensor type.

## CLI

### `zpe-iot compress INPUT --preset PRESET --output OUTPUT [--mode MODE] [--threshold THR]`
Compress CSV to `.zpk` bytes.

### `zpe-iot decompress INPUT --output OUTPUT`
Decode `.zpk` to CSV.

### `zpe-iot benchmark INPUT --compare zstd,lz4,zlib [--preset PRESET]`
Run local comparison against general compressors.

### `zpe-iot info INPUT`
Print packet metadata and compression stats.
