# Phase 7 Native Wheel Verification

Date: 2026-03-21
Phase: 07 native wheel and runtime packaging

## Purpose

Supersede the bounded pure-Python wheel proof with a real native-bundled arm64 wheel that exposes `native_available = true` on cold install while preserving the dev-tree fallback path.

## Packaging Pattern

The wheel surface now follows the ZPE-IMC-style split between:

- the Python package as the distribution surface under `python/`
- a dedicated PyO3 native extension crate under `python/native/`
- `_native.py` preferring the installed extension module and falling back to the dev-tree CFFI-loaded dylib only when the extension is absent

The Python build authority was moved to `python/pyproject.toml` with:

- `build-backend = "maturin"`
- `manifest-path = "native/Cargo.toml"`
- `python-source = "."`
- `module-name = "zpe_iot._zpe_iot_native"`

## Build Evidence

Successful direct maturin build:

- command:
  - `cd python && /tmp/zpe-iot-phase5-arm64-venv/bin/python -m maturin build --release --interpreter /tmp/zpe-iot-phase5-arm64-venv/bin/python --out dist`
- result:
  - `python/dist/zpe_iot-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`

Successful packaging frontend build:

- command:
  - `cd python && /tmp/zpe-iot-phase5-arm64-venv/bin/python -m build`
- result:
  - `python/dist/zpe_iot-0.1.0.tar.gz`
  - `python/dist/zpe_iot-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`

## Cold Install Proof

Fresh environment:

- `/tmp/zpe-iot-phase7-wheel`

Install command:

- `/tmp/zpe-iot-phase7-wheel/bin/pip install python/dist/zpe_iot-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`

Cold import verdict:

- package import path:
  - `/private/tmp/zpe-iot-phase7-wheel/lib/python3.14/site-packages/zpe_iot/__init__.py`
- `native_available`:
  - `true`
- loaded native module:
  - `zpe_iot._zpe_iot_native`
- backend metadata:
  - `backend = rust`
  - `origin = pyo3_native_extension`
  - `fallback_used = false`

## CLI Smoke

Fresh-environment CLI checks:

- `zpe-iot compress --help`: exit `0`
- `zpe-iot chemosense-smoke --json`: exit `0`

Compact smoke payload:

- `fused_event_count = 2`
- `fused_word_count = 31`
- `touch_placeholder_removed = true`

## Source-Tree Regression Slice

- `cargo test --release --manifest-path core/Cargo.toml`: PASS
- `python/tests/test_native.py python/tests/test_cli.py`: `14 passed`
- the Phase 6 benchmark and strict-DT authority surfaces remain green after the packaging changes

## Verdict

Phase 7 is closed on the arm64 macOS truth machine.

- the current wheel is no longer pure-Python only
- cold install now exposes `native_available = true`
- the runtime can import and use the bundled extension from `site-packages`
- the dev-tree CFFI fallback still exists for local workflows where the extension is not installed
