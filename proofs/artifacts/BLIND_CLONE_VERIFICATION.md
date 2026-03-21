# Blind-Clone Verification

Date: 2026-03-21
Phase: 03 portability, blind-clone, and wheel verification

## Objective

Verify that the current source tree can reproduce the essential install and validation surface in an equivalently clean workspace without relying on hidden local state from the dirty development lane.

## Clean Workspace

- workspace root: `/tmp/zpe-iot-phase3-clean.UhxVIC/repo`
- source came from a fresh `rsync` copy of the current repo
- excluded from the copy: `.git`, `release`, `validation/results`, `core/target`, `python/dist`, and transient caches
- retained on purpose: `validation/datasets/raw`, transform artifacts, manifests, and the rest of the source tree needed for truthful validation

## Clean-Workspace Install And Smoke Path

Inside the clean workspace:

- created a fresh venv at `/tmp/zpe-iot-phase3-clean-venv`
- installed the Python package from source
- ran `zpe-iot compress`, `info`, `decompress`, `diagnostics`, and `chemosense-smoke`

Smoke result:

- all CLI commands exited `0`
- sample smoke input: `256` rows
- packet size: `196` bytes
- compression ratio: `10.448979591836734x`
- `chemosense-smoke` reported `smell_stroke_count = 2` and `fused_event_count = 2`

The clean CLI smoke path works even before a native library is built in that workspace.

## Initial Portability Failure

The first strict targeted DT subset in the clean workspace failed on exactly two items:

- `DT-11 Cross-Platform Parity`: `Native library unavailable`
- `DT-25 Chemosense Malformed Resilience`: missing local `bench_summary_chemosense_*.json`

These were hidden operational assumptions, not authority-metric regressions:

- parity requires a Rust build in the clean workspace so `_native` can actually load a library there
- `DT-25` expects a compact Chemosense benchmark summary artifact if `validation/results` was intentionally excluded from the clean copy

## Closure Steps

To close those assumptions honestly in the clean workspace:

- ran `cargo test --manifest-path core/Cargo.toml`
- ran `ZPE_IOT_BASELINE_TAG=draconian_20260214C python validation/benchmarks/run_chemosense_benchmarks.py`
- reran `python validation/destruct_tests/run_all_dts.py --dt 10 11 13 17 25 --strict-gates`

## Final Blind-Clone Result

Final targeted DT subset:

- `DT-10`: PASS
- `DT-11`: PASS
- `DT-13`: PASS
- `DT-17`: PASS
- `DT-25`: PASS
- `mandatory_failures: []`

Saved clean-workspace DT artifact:

- `/tmp/zpe-iot-phase3-clean.UhxVIC/repo/validation/results/dt_results_20260321T150347.json`

## Honest Boundary

`VALD-02` is closed.

What this proves:

- an equivalently clean workspace can reproduce the essential install and validation surface
- the current source tree does not need the dirty local lane to pass the decisive portability subset

What this does not claim:

- it does not claim that a cold wheel includes the native library
- it does not claim that `validation/results` can be omitted if a DT path explicitly depends on locally generated benchmark-summary metadata
- it does not weaken the March 21, 2026 authority benchmark or strict-DT surfaces
