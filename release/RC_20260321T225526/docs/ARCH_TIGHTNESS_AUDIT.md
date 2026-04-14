# Architecture Tightness Audit

Date: 2026-02-14
Scope: `core/src/codec.rs`, `core/src/bitpack.rs`, `core/src/rle.rs`, examples/scripts, mandatory fallback paths.

## Summary

This audit removed or constrained circuitous paths that affected hot-path clarity, demo truthfulness, and gate determinism.

## Before -> After Changes

1. Decode hot-path branch tightening (`core/src/codec.rs`)
- Before: `decode_into` evaluated mode branch logic inside a token loop.
- After: mode dispatch is hoisted once, with dedicated fast/balanced decode loops.
- Effect: fewer repeated conditionals in hot decode path and clearer mode-specific flow.

2. Quickstart redundant encode removed (`README.md`)
- Before: Python quickstart encoded the same signal twice (one for packet, one for CR print).
- After: single `stream` object is reused for both packet bytes and CR.
- Effect: no accidental duplicate work in primary API example.

3. Customer demo baseline completeness (`scripts/customer_demo.py`)
- Before: reported only zpe-iot metrics and ROI.
- After: mandatory side-by-side report includes zpe-iot vs zstd/LZ4/zlib in one artifact.
- Effect: aligns demo output with launch gate truth constraints and removes one-sided reporting path.

4. Missing-prerequisite semantics kept explicit (`validation/destruct_tests/dt06_ram_budget.py`, `validation/destruct_tests/dt16_benchmark_regression.py`)
- Before: historical risk of permissive fallback interpretation.
- After: missing prerequisites are explicitly `SKIPPED`; strict runner treats mandatory `SKIPPED` as gate-failing.
- Effect: no silent PASS-equivalent fallback in mandatory paths.

## Complexity Delta (Qualitative)

- `decode_into` mode branching:
  - Before: branch check within token loop body.
  - After: single top-level dispatch, two linear token loops.
- Quickstart API flow:
  - Before: `encode` called twice on same input.
  - After: `encode` called once.

## Trade-offs

- Splitting decode flow duplicates a small amount of loop body structure, but improves local reasoning and branch predictability.
- Customer demo now imports comparator dependencies (`zstandard`, `lz4`) and performs more compute to provide truthful side-by-side output.

## Evidence Paths

- `<REPO_ROOT>/core/src/codec.rs`
- `<REPO_ROOT>/README.md`
- `<REPO_ROOT>/scripts/customer_demo.py`
- `<REPO_ROOT>/validation/destruct_tests/dt06_ram_budget.py`
- `<REPO_ROOT>/validation/destruct_tests/dt16_benchmark_regression.py`

## Update 2026-02-19 (Phase E2)

### Before -> After

1. Fidelity math scattered across DT and benchmark scripts
- Before: ad-hoc NRMSE formulas existed in multiple files with implicit normalization assumptions.
- After: shared semantics module `validation/metrics/fidelity.py` centralizes named modes and labels.
- Effect: one import path controls both equations and publication labels.

2. Benchmark table label ambiguity
- Before: customer-facing benchmark tables used plain `NRMSE`.
- After: generated reports print explicit `NRMSE(window-normalized)` labels from shared constants.
- Effect: prevents commercial misinterpretation of DT vs benchmark fidelity numbers.

3. DT fidelity expression drift risk
- Before: DT scripts implemented local normalization details.
- After: DT-01/DT-04/DT-12 consume named modes (`dataset-normalized` vs `window-normalized`) from shared module.
- Effect: no hidden divergence between gate math and documented semantics.

### Added Evidence Paths

- `<REPO_ROOT>/validation/metrics/fidelity.py`
- `<REPO_ROOT>/docs/FIDELITY_SEMANTICS.md`
- `<REPO_ROOT>/validation/destruct_tests/dt01_fidelity.py`
- `<REPO_ROOT>/validation/destruct_tests/dt04_noise_robustness.py`
- `<REPO_ROOT>/validation/destruct_tests/dt12_preset_coverage.py`
- `<REPO_ROOT>/validation/benchmarks/_common.py`
- `<REPO_ROOT>/validation/benchmarks/run_benchmarks.py`

## Update 2026-02-20 (Chemosense Hardening Delta)

### Before -> After

1. Native encode FFI path list materialization
- Before: `python/zpe_iot/_native.py` converted every NumPy window via `x.tolist()` before FFI encode.
- After: zero-copy `cffi.from_buffer` path on contiguous float64 arrays.
- Effect: removed per-call Python list allocation on hot native encode path; DT-09 latency returned to PASS.

2. Fusion scheduler multi-scan parsing
- Before: `FusionScheduler.ingest_stream` scanned the same raw stream 3 times (`taste`, `smell`, `touch` extractors).
- After: unified single-pass packet extraction with modality-specific consumers.
- Effect: reduced circuitous repeated packet scans; measured fusion ingest p50 improvement in chemosense perf profile artifact.

3. API/CLI smoke primitive divergence
- Before: CLI smoke flow hand-assembled modality logic separately from Python API entrypoints.
- After: shared contract primitive `zpe_iot.chemosense.run_smoke_flow` is used by CLI and API.
- Effect: one deterministic semantic path for smoke checks and contract tests.

### Added Evidence Paths

- `<REPO_ROOT>/python/zpe_iot/_native.py`
- `<REPO_ROOT>/python/zpe_iot/chemosense/taste/fusion_scheduler.py`
- `<REPO_ROOT>/python/zpe_iot/chemosense/contract.py`
- `<REPO_ROOT>/validation/benchmarks/profile_chemosense.py`
- `<REPO_ROOT>/validation/results/perf_profile_chemosense_20260220T035037.json`
- `<REPO_ROOT>/docs/perf/chemosense_profile_20260220T035037.md`
