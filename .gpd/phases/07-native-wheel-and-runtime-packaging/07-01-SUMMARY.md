# Phase 7 Plan 07-01 Summary

Date: 2026-03-21
Status: complete

## What This Plan Did

- created a dedicated PyO3 native extension crate under `python/native/` instead of trying to overload the existing C ABI crate
- moved the Python build authority in `python/pyproject.toml` to maturin so wheel builds run from the real package root and include the full `zpe_iot` package surface
- updated `_native.py` to prefer the installed extension module and fall back to the dev-tree CFFI-loaded dylib only when the extension is absent
- built the arm64 wheel via both direct maturin and `python -m build`
- verified cold-install import, runtime native availability, and CLI smoke in a fresh environment

## Outcome

Phase 7 closed as a real packaging upgrade.

- the built wheel now contains both the Python package and the bundled extension module
- fresh-install proof in `proofs/artifacts/PHASE7_NATIVE_WHEEL_VERIFICATION_20260321.md` shows:
  - `native_available = true`
  - native module `zpe_iot._zpe_iot_native`
  - cold-install CLI smoke exit `0`
- `python/tests/test_native.py python/tests/test_cli.py`: `14 passed`
- the build surface now works through:
  - `python -m maturin build --release ...`
  - `python -m build`

## Immediate Next Step

Execute Phase 8 as the authority-surface expansion lane. The next gate is to add DS-09 through DS-12 as real-public datasets with provenance, preprocessing, manifest entries, and a fresh expanded benchmark rerun.

```yaml
gpd_return:
  status: completed
  files_written:
    - .gpd/phases/07-native-wheel-and-runtime-packaging/07-01-SUMMARY.md
    - proofs/artifacts/PHASE7_NATIVE_WHEEL_VERIFICATION_20260321.md
    - python/native/Cargo.toml
    - python/native/src/lib.rs
    - python/pyproject.toml
    - python/zpe_iot/_native.py
    - .github/workflows/build_wheels.yml
  issues: []
  next_actions:
    - Plan and execute Phase 8 with the four real-public datasets named in the closure brief
    - Keep the current arm64 wheel proof as the packaging baseline for later multi-platform work
    - Revisit packaging warning cleanup only if the final gate requires a warning-free surface
```
