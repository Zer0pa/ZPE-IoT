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
- Mean CR on E1 DS-01..DS-08: 4.37x (`validation/results/bench_summary_E1_real_public_20260220T043931.json`)
- PT-6 E2 status: NOT_AVAILABLE (0 datasets in `validation/results/bench_summary_E2_real_customer_20260220T043931.json`)

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

## Chemosense Extension (Smell + Taste + Touch + Mental)
The Python SDK now includes `zpe_iot.chemosense` for multimodal packetization and deterministic fusion scheduling:

```python
from zpe_iot.chemosense import (
    encode_mental_payload,
    encode_smell_payload,
    encode_taste_payload,
    encode_touch_payload,
)

smell_words = encode_smell_payload({
    "metadata": {"sniff_hz": 3},
    "strokes": [{"category": "FLORAL", "pleasantness_start": 4, "intensity_start": 1, "directions": [0, 2, 4]}],
})
taste_words = encode_taste_payload({
    "adaptive": True,
    "events": [{"quality_vector": [7, 1, 1, 0, 3], "temporal_directions": [1, 1, 0, 0, 0, 7, 6, 6], "intensity_end": 4}],
})
touch_words = encode_touch_payload({
    "strokes": [{"receptor": "SA_I", "region": "INDEX_TIP", "directions": [0, 2, 4], "pressure_profile": [2, 3, 2]}],
})
mental_words = encode_mental_payload({
    "strokes": [{"form_class": "SPIRAL", "symmetry": "D4", "direction_profile": "COMPASS_8", "start": [128, 128], "directions": [0, 1, 2, 3]}],
})
```

CLI smoke check:
```bash
zpe-iot chemosense-smoke --json
python -m zpe_iot.cli chemosense-smoke --json
```

Latest chemosense benchmark artifact:
- `validation/results/bench_summary_chemosense_20260220T043714.json`
- Evidence mix: smell/taste/fusion = E1, touch/mental = E0
- Comparator outcome in this envelope: zlib wins 5/5 (no superiority claim for chemosense CR)

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
