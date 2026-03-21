# Phase 2 Bridge Solution Receipt

Date: 2026-03-21
Automation: Hourly PRD Closer

## Sovereign Anchors Reviewed

- `validation/results/release_preflight_report_20260320T154022.json`: `17 PASS`, `0 FAIL`, `1 DEFERRED`, `0 critical failures`
- `validation/results/dt_results_20260320T174518.json`: strict DT authority remains green
- `validation/results/bench_summary_E1_real_public_20260320T174720.json`: `mean CR 4.369104600542837x`, `PT-6 6/8`
- `proofs/artifacts/PHASE2_GAP_BUDGET_20260321.json`
- `proofs/artifacts/PHASE2_OVERHEAD_DECOMPOSITION_20260321.json`
- `proofs/artifacts/PHASE2_CANDIDATE_SHORTLIST_20260321.md`

## PRD State

The PRD remains open.

Release truth is materially improved on the March 20 authority surface, but the governing wedge gate is still open because:

- `mean CR` is still below the sovereign `>= 5.0x` gate
- `PT-6` is still `6/8`, below the sovereign `>= 7/8` gate
- blind-clone verification is still open
- cold-wheel verification is still open
- truthful status-surface reconciliation is not yet the closeout bottleneck because the wedge gate is still unsettled

## Single Highest-Leverage Open Blocker

The highest-leverage open blocker is now the corrected bridge-plan gap:

- the new code-backed budget artifact proves `single_bridge_dataset = null`
- the March 20 E1 surface does not support `DS-02` as a one-dataset bridge
- the decomposition instead shows a smooth low-entropy cluster on `DS-05`, `DS-02`, and `DS-08`, with `DS-06` still outside that family but too large to ignore

This remains the best next blocker because March 20 authority math now says all of these are true at once:

- `DS-01 + DS-05` closure alone only reaches about `4.7081x`
- the remaining budget after that ceiling is about `2.3351`
- no single winner-side dataset can repay that residual budget alone
- the smallest code-backed winning bridge set is `DS-02 + DS-06 + DS-08`

If the project cannot prove a smooth-series slice on `DS-05`, `DS-02`, and `DS-08` and then show that the residual path through `DS-06` is still honest, the wedge path should be downgraded early instead of widened into another diffuse uplift sweep.

## Concrete Solution Tasks

### Task 1: Lock the corrected bridge math in executable output

Owner files:

- `validation/benchmarks/phase2_gap_budget.py`
- `proofs/artifacts/PHASE2_GAP_BUDGET_20260321.json`

Required work:

- parse `bench_summary_E1_real_public_20260320T174720.json`
- rank winners by `gap_to_5x`
- emit current total CR budget, target budget, missing budget, the `DS-01 + DS-05` ceiling, and the residual after that ceiling
- emit an explicit `single_bridge_dataset = null` verdict when no one dataset clears that residual budget
- emit the smallest winning bridge set that would clear the residual if it reached `5.0x`

Acceptance gate:

- no hand-carried bridge math remains in Phase 2 summaries
- the false `DS-02` single-bridge premise is replaced with the measured result from code

### Task 2: Measure packet composition before proposing mechanism work

Owner files:

- `validation/benchmarks/phase2_overhead_decomposition.py`
- `proofs/artifacts/PHASE2_OVERHEAD_DECOMPOSITION_20260321.json`

Required work:

- use the real authority subset in this order: `DS-05`, `DS-02`, `DS-06`, `DS-08`, `DS-01`
- for each dataset, emit `header_bytes`, `crc_bytes`, `token_bytes`, `payload_bytes`, `bytes_per_256_window`, `zero_delta_ratio`, `zero_token_ratio`, and the dominant sink label
- compare `DS-05` first against `DS-02`, `DS-08`, `DS-06`, and `DS-01`
- emit the smooth-series cluster explicitly rather than assuming `DS-02` is the only bridge case

Acceptance gate:

- the artifact answers which datasets actually share the `DS-05` sink family
- the answer is grounded in measured packet composition, not preset intuition

### Task 3: Shortlist only mechanism families that survive the corrected bridge verdict

Owner file:

- `proofs/artifacts/PHASE2_CANDIDATE_SHORTLIST_20260321.md`

Required work:

- create the shortlist only after Tasks 1 and 2 complete
- include only candidate families that target `DS-05` plus the measured smooth-series bridge set
- record expected authority benefit, DT risk, and the smallest proving subset before any full E1 rerun

Reject by default:

- `DS-02`-alone bridge narratives
- `DS-01`-only fixes
- WI-1 / ZH-1 wrapper retuning loops

Acceptance gate:

- each candidate has an explicit go/no-go rule tied to the March 20 authority gate

### Task 4: Spend the next full E1 rerun only if the subset says it is worth it

Required rule:

- no full E1 rerun unless the smooth-series subset verdict stays positive and the shortlisted mechanism still leaves a plausible route to both `mean CR >= 5.0x` and `PT-6 >= 7/8` with no DT regression expectation

If the corrected bridge verdict is negative:

- stop expanding uplift work
- record that the wedge path is not currently justified on the unchanged E1 surface
- move the project toward an honest bounded failure verdict instead of a broader search

## What Changed In This Run

- Re-reviewed the March 20 authority anchors and current `.gpd` state.
- Implemented `validation/benchmarks/phase2_gap_budget.py` and `validation/benchmarks/phase2_overhead_decomposition.py`.
- Proved from code that `DS-02` is not a single bridge dataset on the March 20 E1 surface.
- Reframed the next blocker as a triad-aware subset plan and wrote the compact candidate shortlist at `proofs/artifacts/PHASE2_CANDIDATE_SHORTLIST_20260321.md`.

## What Remains Blocked

- `mean CR >= 5.0x` on unchanged E1 is still unproven
- `PT-6 >= 7/8` is still unproven
- blind-clone verification is still open
- cold-wheel verification is still open

## Next Best Task

Implement `validation/benchmarks/phase2_smooth_series_probe.py` and test one monotone payload-side mechanism on `DS-05`, `DS-02`, and `DS-08` before any full E1 rerun.
