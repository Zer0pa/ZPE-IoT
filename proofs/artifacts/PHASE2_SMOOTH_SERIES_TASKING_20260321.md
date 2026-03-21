# Phase 2 Smooth-Series Tasking

Date: 2026-03-21
Automation: Hourly PRD Closer

## Sovereign Anchors

- `validation/results/release_preflight_report_20260320T154022.json`: `17 PASS`, `0 FAIL`, `1 DEFERRED`, `0 critical failures`
- `validation/results/dt_results_20260320T174518.json`: strict DT authority remains green
- `validation/results/bench_summary_E1_real_public_20260320T174720.json`: `mean CR 4.369104600542837x`, `PT-6 6/8`
- `proofs/artifacts/PHASE2_GAP_BUDGET_20260321.json`
- `proofs/artifacts/PHASE2_OVERHEAD_DECOMPOSITION_20260321.json`
- `proofs/artifacts/PHASE2_CANDIDATE_SHORTLIST_20260321.md`

## PRD State

The PRD remains open.

The governing wedge gate is still blocked because:

- `mean CR` is still below the sovereign `>= 5.0x` gate
- `PT-6` is still `6/8`, below the sovereign `>= 7/8` gate
- blind-clone verification is still open
- cold-wheel verification is still open
- status-surface reconciliation remains downstream of the wedge result, not a substitute for it

## Single Highest-Leverage Open Blocker

The single highest-leverage blocker is no longer bridge math. That part is already frozen by code-backed March 20 artifacts.

The live blocker is:

- Phase 2 still lacks one measured smooth-series prototype on `DS-05`, `DS-02`, and `DS-08` that can prove whether the only shared payload family has a real DT-safe uplift path before the project spends either a `DS-06` branch or a full E1 rerun

Why this blocker is sovereign:

- `DS-01 + DS-05` closure alone only lifts the mean to about `4.7081x`
- the residual budget after that ceiling is still about `2.3351`
- `DS-05`, `DS-02`, and `DS-08` are the only currently measured shared sink family
- `DS-06` remains outside that family, so it should not absorb effort until the smooth-series slice proves it can move the remaining budget honestly

## Concrete Solution Tasks

### Task 1: Build the smallest admissible smooth-series probe

Owner files:

- `validation/benchmarks/phase2_smooth_series_probe.py`
- `proofs/artifacts/PHASE2_SMOOTH_SERIES_PROBE_20260321.json`

Required work:

- test exactly one monotone payload-side mechanism on `DS-05`, `DS-02`, and `DS-08`
- emit baseline versus candidate `bytes_per_256_window`, `payload_bytes`, and total compressed bytes
- keep packet wrappers, native boundary behavior, and benchmark surface unchanged

Acceptance gate:

- every target dataset reports the same measurement schema
- the mechanism is payload-side only, not wrapper retuning

Hard stop:

- stop immediately if the candidate needs a wrapper change or fails to move at least two of the three target datasets

### Task 2: Run the subset monotonicity and fidelity guardrails before any expansion

Owner files:

- `validation/benchmarks/phase2_smooth_series_probe.py`
- `proofs/artifacts/PHASE2_SMOOTH_SERIES_PROBE_20260321.json`

Required work:

- run the authority-subset monotonicity check on the candidate outputs
- record whether any `DT-10` style inversion appears on `DS-05`, `DS-02`, or `DS-08`
- record the candidate fidelity deltas using the current benchmark contract rather than a softer proxy

Acceptance gate:

- no monotonic inversion is introduced on the subset
- no benchmark-contract fidelity drift appears that would make the gain unusable

Hard stop:

- if the subset fails `DT-10` logic or requires a relaxed fidelity interpretation, terminate the mechanism path and do not widen the run

### Task 3: Recompute the residual budget from measured subset gains

Owner files:

- `proofs/artifacts/PHASE2_SMOOTH_SERIES_PROBE_20260321.json`
- `proofs/artifacts/PHASE2_GAP_BUDGET_20260321.json`

Required work:

- convert the measured subset gains into updated mean-CR budget math
- decide whether `DS-06` is still mandatory for any plausible path to `>= 5.0x`
- state explicitly whether the subset leaves a live route to `PT-6 >= 7/8`

Acceptance gate:

- the updated residual is derived from measured subset output, not estimated narrative
- the artifact ends with an explicit `DS-06 required` or `DS-06 not yet required` verdict

Hard stop:

- if the residual still depends on an unmeasured second mechanism with no honest path, record an early wedge downgrade instead of opening more search

### Task 4: Spend `DS-06` only if Task 3 leaves a live route

Owner files:

- `validation/benchmarks/phase2_high_variance_probe.py`
- `proofs/artifacts/PHASE2_HIGH_VARIANCE_PROBE_20260321.json`

Required work:

- only after Task 3 passes, test one `DS-06`-specific high-variance mechanism
- keep the proving surface narrow and explicitly separate from the smooth-series family

Acceptance gate:

- the `DS-06` spend is justified by residual math, not by general curiosity

Hard stop:

- no full E1 rerun unless the combined subset evidence still supports both `mean CR >= 5.0x` and `PT-6 >= 7/8` with no expected DT regression

## Rejected Directions

- more WI-1 or ZH-1 wrapper retuning
- any `DS-02`-alone bridge narrative
- full E1 reruns before the smooth-series subset closes
- doc-only closure work while the governing wedge gate is still open
