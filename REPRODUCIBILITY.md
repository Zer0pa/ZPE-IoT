# Reproducibility

## Canonical Inputs

- `validation/datasets/manifest.json`
- `validation/datasets/manifest_chemosense.json`
- `validation/datasets/DS-01/data.npz`
- `validation/datasets/DS-02/data.npz`
- `validation/datasets/DS-03/data.npz`
- `validation/datasets/DS-04/data.npz`
- `validation/datasets/DS-05/data.npz`
- `validation/datasets/DS-06/data.npz`
- `validation/datasets/DS-07/data.npz`
- `validation/datasets/DS-08/data.npz`
- `validation/datasets/DS-09/data.npz`
- `validation/datasets/DS-10/data.npz`
- `validation/datasets/DS-12/data.npz`
- `python/tests/fixtures/golden_packets_v1.json`
- `python/tests/fixtures/benchmark_label_cases.json`

## Golden-Bundle Hash

This field will be populated by the `receipt-bundle.yml` workflow in Wave 3.

## Verification Command

```bash
git clone https://github.com/Zer0pa/ZPE-IoT zpe-iot
cd zpe-iot
python -m pip install -e './python[dev]'
cargo test --manifest-path core/Cargo.toml --release
python validation/destruct_tests/run_all_dts.py --strict-gates
```

## Supported Runtimes

- Python package runtime on Python 3.10+
- Rust core crate on the Rust 2021 toolchain
- PyO3/maturin native extension build path for the Python package
- C integration surface via `c/zpe_iot.h` and the static library artifacts
