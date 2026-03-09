# zpe-iot — Sensor Compression with E1 Evidence (Mean 4.37x)

**GPU-free. Deterministic. 4 KB RAM. Tuned for IoT time-series.**

## Quick Start (Python)
```python
import numpy as np
import zpe_iot

signal = np.sin(np.linspace(0, 20, 1024))
stream = zpe_iot.encode(signal, preset="vibration")
packet = stream.to_bytes()
restored = zpe_iot.decode(packet)
print("CR:", stream.compression_ratio)
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
- PT-6 FINAL (E1): PASS (6/8 wins)
- Mean CR on E1 DS-01..DS-08: 4.37x (`validation/results/bench_summary_E1_real_public_20260219T030604.json`)
- PT-6 E2 status: NOT_AVAILABLE (0 datasets in `validation/results/bench_summary_E2_real_customer_20260219T030604.json`)

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

## Chemosense Extension (Smell + Taste)
The Python SDK now includes `zpe_iot.chemosense` for smell/taste packetization and deterministic fusion scheduling:

```python
from zpe_iot.chemosense import smell, taste

smell_words = smell.encode_smell_strokes([smell.synthetic_sniff_stroke(smell.OdorCategory.FLORAL)])
taste_event = taste.zlayered_event_from_vector((7, 1, 1, 0, 3))
taste_words = taste.pack_taste_zlayered([taste_event], adaptive=True)
```

CLI smoke check:
```bash
zpe-iot chemosense-smoke --json
```

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
