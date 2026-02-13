# zpe-iot — Compress Sensor Data 5-10x on Any MCU

**GPU-free. Deterministic. 4 KB RAM. Tuned for IoT time-series.**

## Quick Start (Python)
```python
import numpy as np
import zpe_iot

signal = np.sin(np.linspace(0, 20, 1024))
packet = zpe_iot.encode(signal, preset="vibration").to_bytes()
restored = zpe_iot.decode(packet)
print("CR:", zpe_iot.encode(signal, preset="vibration").compression_ratio)
```

## Quick Start (Rust)
```rust
use zpe_iot::{encode, decode_into, Preset};

let cfg = Preset::Vibration.config();
let stream = encode::<2048>(&samples, &cfg)?;
let mut out = [0.0_f64; 1024];
let n = decode_into(&stream, &mut out)?;
```

## Benchmarks
See [`docs/BENCHMARKS.md`](docs/BENCHMARKS.md) for full methodology, per-dataset tables, and charts.

Current summary (latest local run):
- PT-6: pass (zpe-iot wins on >50% of DS-01..DS-08)
- Mean CR across DS-01..DS-08: see `validation/results/bench_summary_*.json`

![CR comparison](docs/benchmarks/cr_comparison.png)

## Supported Sensor Types
| Preset | Use Case |
|---|---|
| `temperature` | Thermistor/weather trend data |
| `vibration` | Machinery/bearing vibration |
| `accelerometer` | IMU motion streams |
| `pressure` | Barometric/process pressure |
| `gps_track` | GPS trajectory deltas |
| `voltage` | Electrical telemetry |
| `current` | Current waveforms |
| `flow` | Process flow sensors |
| `generic` | Unknown/mixed sensors |

## Why Not Just Use zstd/LZ4?
General compressors often achieve 2-3x on raw sensor streams.
zpe-iot uses signal-aware directional quantisation + RLE to push higher CR on IoT patterns while preserving deterministic embedded behavior.

## Installation
```bash
pip install zpe-iot
cargo add zpe-iot
```

## License
MIT (free for evaluation and small deployments).
Commercial licensing for large deployments: contact `sales@zer0pa.com`.

## ROI Calculator
Use [`scripts/savings_calculator.py`](scripts/savings_calculator.py) or see [`docs/BENCHMARKS.md#roi-calculator`](docs/BENCHMARKS.md#roi-calculator).
