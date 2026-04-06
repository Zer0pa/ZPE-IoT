# Reproducing ZPE-IoT

This document captures the cold-clone verification path for the current repo
surface. It covers the editable development install, the Python and Rust test
surfaces, and the local wheel install path.

## Prerequisites

- Python `3.10+`
- Rust toolchain with `cargo`
- macOS or Linux shell environment

## 1. Clone The Repository

```bash
git clone https://github.com/Zer0pa/ZPE-IoT.git zpe-iot
cd zpe-iot
```

## 2. Create An Isolated Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

## 3. Install The Editable Python Package

```bash
cd python
python -m pip install -e ".[dev]"
cd ..
```

Repo-root shortcut:

```bash
make install
```

## 4. Run The Python Test Surface

```bash
cd python
python -m pytest tests/ -v
cd ..
```

Repo-root shortcut:

```bash
make test
```

## 5. Run The Rust Test Surface

```bash
cd core
cargo test
cd ..
```

## 6. Build A Wheel

```bash
cd python
python -m maturin build --release --out dist/
cd ..
```

Repo-root shortcut:

```bash
make wheel
```

Expected output:

- `python/dist/zpe_iot-*.whl`

## 7. Verify The Wheel Install Path

```bash
python3 -m venv /tmp/zpe-iot-wheel-check
source /tmp/zpe-iot-wheel-check/bin/activate
python -m pip install --upgrade pip
python -m pip install "$(ls python/dist/zpe_iot-*.whl | head -1)"
python - <<'PY'
from zpe_iot import decode, encode
import numpy as np

samples = np.linspace(0.0, 1.0, 256, dtype=np.float64)
packet = encode(samples, preset="generic").to_bytes()
restored = decode(packet)
print({"packet_bytes": len(packet), "restored_samples": len(restored)})
PY
deactivate
```
