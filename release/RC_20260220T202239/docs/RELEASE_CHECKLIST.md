# Release Checklist (Deferred Publish)

Date: 2026-02-19

## RC Build Preconditions

- [x] `cargo test` passes
- [x] `cargo clippy -- -D warnings` passes
- [x] `pytest -q` passes with coverage >= 85%
- [x] strict DT run passes (`SKIPPED=0` for mandatory set)
- [x] benchmark split artifacts regenerated (E0/E1/E2)
- [ ] security scan artifact generated with high/critical = 0
- [ ] SBOM + license manifest + release manifest generated

## Package Validation

- [ ] `python -m build` warning-free
- [ ] fresh-venv install smoke (`compress/info/decompress/benchmark/diagnostics`)
- [x] chemosense CLI smoke passes (`zpe-iot chemosense-smoke --json`)
- [x] chemosense module smoke passes (`python -m zpe_iot.cli chemosense-smoke --json`)
- [x] chemosense contract tests pass (`python/tests/test_chemosense_contract.py`)
- [x] chemosense perf profile artifact generated (`validation/results/perf_profile_chemosense_<timestamp>.json`)
- [x] chemosense benchmark summary artifact generated (`validation/results/bench_summary_chemosense_<timestamp>.json`)
- [x] chemosense provenance manifest verified (`validation/datasets/manifest_chemosense.json`)

## Release Bundle

- [x] `release/RC_CHEMOSENSE_<timestamp>/` (or `release/RC_<timestamp>/`) generated
- [x] bundle manifest hash file generated
- [ ] memory-doc snapshot synced from root into `project_docs/`

## Deferred Steps (Require Explicit User Ratification)

- [ ] push git tag
- [ ] publish to PyPI
- [ ] publish to crates.io
- [ ] outreach execution

## One-Command Preflight

```bash
cd '/Users/prinivenpillay/ZPE IoT/zpe-iot'
bash scripts/release_preflight.sh
```
