# Contributing

## Before You Start

- Read `README.md`, `docs/ARCHITECTURE.md`, and `proofs/FINAL_STATUS.md`.
- Treat code, tests, and proof artifacts as authority over prose.
- Do not upgrade public-facing claims unless the same change set updates the cited evidence paths.

## Development Setup

```bash
cd /path/to/zpe-iot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e './python[dev]'
```

The repo scripts resolve the active interpreter dynamically. `.venv` is an example, not a hard-coded requirement.

## Required Local Checks

Run these before opening a PR:

```bash
cargo test --manifest-path core/Cargo.toml --release
cargo clippy --manifest-path core/Cargo.toml -- -D warnings
python -m pytest -q
python validation/destruct_tests/run_all_dts.py --strict-gates
bash scripts/release_preflight.sh
```

If you touch packaging or the native path, also run:

```bash
python -m build ./python
maturin build --manifest-path python/native/Cargo.toml --release
```

## Contribution Rules

- Do not weaken strict DT gates, benchmark provenance rules, or dataset declarations.
- Do not silently widen the benchmark surface; `DS-11` stays blocked until the repo evidence changes.
- Keep `project_docs/` and older `release/RC_*` bundles as historical lineage.
- Do not add runtime coupling to `ZPE-IMC` unless the code truly requires it.
- Do not run publish steps without explicit owner ratification.
- Do not convert mixed evidence into a pass narrative.
