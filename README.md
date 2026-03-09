# ZPE-IoT

Deterministic sensor compression and chemosense packetization for IoT time-series.

## Current Status

This repository is the canonical private-stage repo candidate for ZPE-IoT.

It is not a public release and it is not yet proven ready for PyPI or crates.io publication.

Latest local managed evidence on 2026-03-09:

- `cargo test --release`: PASS
- `python -m pytest -q`: PASS (`70 passed`, `86.53%` coverage)
- `python validation/destruct_tests/run_all_dts.py --strict-gates`: PASS (`27/27`)
- benchmark refresh: PASS (`PT-6 FINAL`, `6/8` wins, mean E1 CR `4.37x`)
- full release preflight: FAIL
  - `C07_SBOM_RELEASE_MANIFEST`
  - `C10_CHEMOSENSE_CLI_SMOKE` in the last managed run

Start with:

- `proofs/FINAL_STATUS.md`
- `proofs/PROOF_INDEX.md`
- `validation/results/release_preflight_report_20260309T040302.json`
- `docs/BENCHMARKS.md`

## Local Install

Python editable install:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e './python[dev]'
```

Rust crate build/test from source:

```bash
cargo test --manifest-path core/Cargo.toml --release
```

Published install commands are intentionally omitted here because package publication has not been adjudicated.

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
use zpe_iot::{decode_into, encode, Preset};

let cfg = Preset::Vibration.config();
let stream = encode::<2048>(&samples, &cfg)?;
let mut out = [0.0_f64; 1024];
let n = decode_into(&stream, &mut out)?;
```

## Benchmarks

See `docs/BENCHMARKS.md` for the current evidence-labeled benchmark surface.

Latest local summary:

- E1 summary artifact: `validation/results/bench_summary_E1_real_public_20260309T060843.json`
- mean E1 compression ratio: `4.37x`
- PT-6 FINAL: `PASS (6/8 wins)`
- E2 customer claim tier: `NOT_AVAILABLE`

![CR comparison](docs/benchmarks/cr_comparison.png)

## Chemosense Extension

The Python package includes `zpe_iot.chemosense` for smell, taste, touch, and mental packetization.

Module smoke path that passed in the latest managed preflight:

```bash
python -m zpe_iot.cli chemosense-smoke --json
```

The installed `zpe-iot` console-script entrypoint failed in the latest full preflight because the local virtualenv still carried a stale shebang from an older machine path. A local editable reinstall on 2026-03-09 repaired that wrapper and standalone CLI smoke now passes again, but the full managed preflight has not been rerun yet.

Latest chemosense artifacts:

- `validation/results/bench_summary_chemosense_20260309T060913.json`
- `validation/results/perf_profile_chemosense_20260309T060912.json`

## Supported Sensor Presets

| Preset | Use Case |
|---|---|
| `temperature` | Thermistor and weather trend data |
| `vibration` | Machinery and bearing vibration |
| `accelerometer` | IMU motion streams |
| `pressure` | Barometric and process pressure |
| `gps_track` | GPS trajectory deltas |
| `voltage` | Electrical telemetry |
| `current` | Current waveforms |
| `flow` | Process flow sensors |
| `generic` | Unknown or mixed sensors |

## Repo Guide

- `docs/README.md`: docs front door
- `docs/family/`: IMC alignment and compatibility surfaces
- `validation/`: tests, datasets, DTs, benchmarks
- `proofs/`: proof index, status routing, audit pointers
- `project_docs/`: operator mirror and historical planning material

## License

This repo currently ships under MIT. Commercial posture and any publication packaging remain owner-controlled decisions.
