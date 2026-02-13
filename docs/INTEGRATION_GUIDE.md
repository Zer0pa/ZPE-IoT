# ZPE-IoT Integration Guide

## 1. Quick Start (Python)
```python
import numpy as np
import zpe_iot

signal = np.sin(np.linspace(0, 20, 1024))
packet = zpe_iot.encode(signal, preset="vibration").to_bytes()
restored = zpe_iot.decode(packet)
```

## 2. Quick Start (Rust)
```rust
use zpe_iot::{encode, decode_into, Preset};

let cfg = Preset::Vibration.config();
let stream = encode::<2048>(&samples, &cfg)?;
let mut out = [0.0_f64; 1024];
let n = decode_into(&stream, &mut out)?;
```

## 3. Quick Start (C)
```c
zpe_iot_config_t cfg = zpe_iot_preset_vibration();
int32_t n = zpe_iot_encode(samples, n_samples, &cfg, out_bytes, out_cap);
```

## 4. Choosing a Preset
- `temperature`: slow thermistor/weather streams.
- `vibration`: high-rate vibration or machinery.
- `accelerometer`: IMU motion streams.
- `pressure`: barometric and process pressure.
- `gps_track`: GPS coordinate deltas.
- `voltage`/`current`: electrical telemetry.
- `flow`: slow process flow.
- `generic`: fallback for unknown signals.

## 5. Custom Configuration
Tune:
- `threshold`: higher means more compression, lower fidelity.
- `step`: reconstruction granularity (`auto` when 0.0).
- `bands`: directional sensitivity.
- `adaptive`: runtime threshold tracking.

## 6. Embedded Deployment
Use Rust core with `default-features = false, features = ["embedded"]`.
Validate `.data + .bss < 4096` using `dt06_ram_budget.py`.

## 7. Arduino/PlatformIO
Generate `c/zpe_iot.h`, link static lib, call `zpe_iot_encode()` from firmware loop.
See `examples/c/arduino_demo/`.

## 8. MQTT/HTTP Integration
Compress before publish:
1. sample sensor window
2. `encode(...).to_bytes()`
3. publish bytes over MQTT/HTTP
4. decode on receiver

## 9. Calculating ROI
Use `scripts/savings_calculator.py`.
Inputs: device count, KB/day, cellular cost/MB, expected compression.

## 10. Troubleshooting
- `Native library unavailable`: build Rust library (`cargo build --target x86_64-apple-darwin` or your host triple).
- `CRC mismatch`: packet corrupted in transport; retransmit.
- Low CR on noisy data: switch to `fast` mode or tune threshold with `scripts/tuning_wizard.py`.
