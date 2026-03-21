# Phase 5 Plan 05-01 Summary

Date: 2026-03-21
Status: complete

## What This Plan Did

- measured the live Rust and Python values for the drifted `temperature`, `gps_track`, and `flow` presets against the current DT-12 dataset mappings
- rejected the Rust values for all three drifted presets because they achieved higher CR only by violating the current fidelity floor
- updated `core/src/presets.rs` so the Rust canonical table now matches the current Python values for all 9 presets
- added explicit canonical-value tests on both the Rust and Python preset surfaces
- reran the focused Rust and Python verification floor in an `arm64` virtual environment so native parity executed rather than silently skipping

## Outcome

Preset parity is now closed at the table level.

- `temperature` on `DS-03`: Python value `mean CR 7.326961508002325`, `mean NRMSE(window-normalized) 0.007354193885800031`; prior Rust value `mean CR 13.43983641567107`, `mean NRMSE(window-normalized) 0.12254946727250914`
- `gps_track` on `DS-07`: Python value `mean CR 7.682052970794128`, `mean NRMSE(window-normalized) 0.019142264602231656`; prior Rust value `mean CR 12.414678976166474`, `mean NRMSE(window-normalized) 0.18997876544908107`
- `flow` on `DS-03`: Python value `mean CR 7.327150941182731`, `mean NRMSE(window-normalized) 0.007354193885800031`; prior Rust value `mean CR 13.986359460936292`, `mean NRMSE(window-normalized) 0.12591982844341384`
- focused Python verification: `17 passed`, `0 failed`, `0 xfailed`, `0 skipped`
- `DT-12`: PASS for all 9 presets
- Rust verification: `cargo test --release --manifest-path core/Cargo.toml` passed

The only non-obvious verification issue was environment architecture drift: a first temporary venv created with `python3` came up `x86_64`, which caused `_native.available()` to stay false and made native tests skip. Rebuilding the venv with `python` produced an `arm64` environment and restored real native parity execution.

## Immediate Next Step

Execute Phase 6 as one bounded `DS-05` structural closure lane. The gate remains the same: no regression on the March 21, 2026 authority surface.

```yaml
gpd_return:
  status: completed
  files_written:
    - .gpd/phases/05-preset-canonicalization/05-01-SUMMARY.md
    - core/src/presets.rs
    - python/tests/test_presets.py
  issues: []
  next_actions:
    - Plan and execute Phase 6 with one bounded `DS-05` mechanism family selected from current evidence
    - Reuse the `arm64` Phase 5 virtual environment pattern for any native-dependent Python verification in later phases
    - Keep the March 21, 2026 authority benchmark as the sovereign downgrade gate for every follow-on experiment
```
