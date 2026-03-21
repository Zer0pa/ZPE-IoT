# Phase 2 Bridge Execution Contract

Date: 2026-03-20
Phase: 02 targeted compression uplift

## Sovereign Anchors

- `validation/results/release_preflight_report_20260320T154022.json`: `17 PASS`, `0 FAIL`, `1 DEFERRED`, `0 critical failures`
- `validation/results/dt_results_20260320T174518.json`: strict DT remains green
- `validation/results/bench_summary_E1_real_public_20260320T174720.json`: `mean CR 4.369104600542837x`, `PT-6 6/8`
- `proofs/artifacts/LOSS_DIAGNOSIS.md`: `DS-01` and `DS-05` are not simple preset-tuning misses
- `proofs/artifacts/PHASE2_DS05_DS02_BRIDGE_TASKING_20260320.md`: `DS-02` is the only single winning dataset with enough current headroom to cover the residual budget after the `DS-01` plus `DS-05` ceiling

## Governing Blocker

The PRD is still open because the benchmark wedge gate is still below sovereign target. The single highest-leverage unresolved blocker is now:

- Phase 2 still lacks measured proof of whether `DS-05` and `DS-02` share one DT-safe byte-sink mechanism

Until that is answered, every uplift path is still speculative.

## Execution Order

1. `validation/benchmarks/phase2_gap_budget.py`
2. `validation/benchmarks/phase2_overhead_decomposition.py`
3. `proofs/artifacts/PHASE2_CANDIDATE_SHORTLIST_20260320.md`

No full E1 rerun is allowed before steps 1 and 2 show a plausible recovery path.

## Concrete Tasks

### Task A: Freeze the residual-budget truth in code

Create `validation/benchmarks/phase2_gap_budget.py`.

Required outputs:

- dataset ranking by recoverable headroom
- current total CR budget and target total CR budget
- `DS-01` plus `DS-05` ceiling
- residual budget after that ceiling
- `DS-05 + DS-02 + DS-01` theoretical ceiling
- explicit verdict that `DS-02` is or is not sufficient as the single bridge dataset

Done when:

- the bridge math is reproducible from code instead of hand-carried into docs

### Task B: Answer the bridge question with byte accounting

Create `validation/benchmarks/phase2_overhead_decomposition.py`.

Evaluation order:

1. `DS-05`
2. `DS-02`
3. `DS-06`
4. `DS-08`
5. `DS-01`

Required measurements per dataset:

- fixed packet overhead share
- payload share
- bytes per 256-sample window
- zero-delta or flat prevalence when cheaply measurable
- repeat density when cheaply measurable
- simple `same_sink_family` verdict against `DS-05`

The first required conclusion is:

- whether `DS-02` shares the dominant sink family of `DS-05` strongly enough to justify a common prototype

Done when:

- the project has a measured yes or no answer to the `DS-05` / `DS-02` bridge question

### Task C: Gate the shortlist on the bridge verdict

Create `proofs/artifacts/PHASE2_CANDIDATE_SHORTLIST_20260320.md` only after Tasks A and B complete.

Include only candidate families that:

- are DT-safe by construction or have explicit DT-risk containment
- target `DS-05` and at least one bridge dataset
- explain where the residual budget comes from

Reject by default:

- WI-1 or ZH-1 retuning loops
- `DS-01`-only stories
- candidates that improve only one loss without closing the cross-dataset budget path

Done when:

- the shortlist is small enough to execute and explicit enough to reject optimism-by-default

## Hard Stop Rule

Do not spend a full E1 rerun unless the subset evidence supports both of these claims:

- a plausible path to `mean CR >= 5.0x`
- no expected DT regression relative to the March 20 strict DT surface

If the bridge verdict is negative, Phase 2 must downgrade the wedge path early instead of widening the experiment set.

## Next Best Task

Implement `validation/benchmarks/phase2_gap_budget.py`, then implement `validation/benchmarks/phase2_overhead_decomposition.py` with `DS-05` and `DS-02` as the first-class pair.
