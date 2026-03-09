# Release Checklist (Deferred Publish)

Date: 2026-02-19

## RC Build Preconditions

- [ ] `cargo test` passes
- [ ] `cargo clippy -- -D warnings` passes
- [ ] `pytest -q` passes with coverage >= 85%
- [ ] strict DT run passes (`SKIPPED=0` for mandatory set)
- [ ] benchmark split artifacts regenerated (E0/E1/E2)
- [ ] security scan artifact generated with high/critical = 0
- [ ] SBOM + license manifest + release manifest generated

## Package Validation

- [ ] `python -m build` warning-free
- [ ] fresh-venv install smoke (`compress/info/decompress/benchmark/diagnostics`)

## Release Bundle

- [ ] `release/RC_<timestamp>/` generated
- [ ] bundle manifest hash file generated
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
