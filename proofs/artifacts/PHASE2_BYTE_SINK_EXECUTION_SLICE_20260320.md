# Phase 2 Byte-Sink Execution Slice

Date: 2026-03-20
Phase: 02 targeted compression uplift

## Sovereign Anchors

- `validation/results/release_preflight_report_20260320T154022.json`: `17 PASS`, `0 FAIL`, `1 DEFERRED`, `0 critical failures`
- March 20 strict DT authority surface: mandatory DTs still passing
- `validation/results/bench_summary_E1_real_public_20260320T174720.json`: `mean CR 4.369104600542837x`, `PT-6 6/8`

## Single Highest-Leverage Open Blocker

The governing blocker is still the benchmark authority gap, but the immediate highest-leverage missing piece is narrower:

- Phase 2 still has no measured byte-sink decomposition on the authority subset
- without that measurement, every uplift attempt is still guesswork
- the project therefore cannot yet distinguish real cross-dataset recovery paths from another dead-end tuning loop

This is the next blocker to clear before any full E1 rerun.

## Why This Slice Dominates Now

The broad blocker math is already frozen:

- current total CR budget: `34.952836804342696`
- target total CR budget: `40.0`
- missing total CR budget: `5.047163195657304`
- DS-01 plus DS-05-only ceiling: `4.708116425417193x`
- residual cross-dataset budget still required after that ceiling: `2.3350685966624467`

That means the unresolved question is no longer "is there a gap?".

It is:

- where, exactly, are those remaining bytes being spent on the authority subset
- which subset datasets can repay enough of that budget to justify a real prototype
- which candidate families are still admissible under DT and parity constraints

## Concrete Solution Tasks

### Task 1: Lock the residual budget in code

Create `validation/benchmarks/phase2_gap_budget.py`.

Required outputs:

- read `validation/results/bench_summary_E1_real_public_20260320T174720.json`
- emit a compact table for each dataset with current ZPE CR, best current baseline CR, and headroom
- restate the DS-01 plus DS-05-only ceiling and the residual cross-dataset budget still required

Done when:

- the residual budget is reproducible from code rather than manual arithmetic

### Task 2: Measure byte sinks on the authority subset

Create `validation/benchmarks/phase2_overhead_decomposition.py`.

Authority subset:

- `DS-05`
- `DS-02`
- `DS-06`
- `DS-08`
- `DS-01`

Required measurements:

- fixed packet overhead share
- payload-byte share
- per-window payload growth versus raw bytes
- which datasets are dominated by fixed overhead versus payload inefficiency

If token-level structure can be extracted cheaply and deterministically, add:

- flat or zero-delta prevalence
- repeat density
- window-size sensitivity

Done when:

- the project has measured where additional CR can still come from on the authority subset

### Task 3: Convert measurements into a DT-safe shortlist

Create `proofs/artifacts/PHASE2_CANDIDATE_SHORTLIST_20260320.md`.

Only admit candidate families that target `DS-05` and at least one of `DS-02`, `DS-06`, or `DS-08`.

Each candidate entry must state:

- candidate family
- target datasets
- expected budget recovery surface
- exact DT or parity risks
- go or no-go verdict

Reject by default:

- WI-1 or ZH-1 retuning loops already ruled out by `proofs/artifacts/PHASE2_WORKSTREAM_RECHECK_20260320.md`
- DS-01-only or DS-05-only storytelling that cannot close the full E1 budget

Done when:

- the next prototype set is smaller, explicit, and contract-safe

### Task 4: Gate the first prototype before a full rerun

Subset evaluation order:

1. `DS-05`
2. `DS-02`
3. `DS-06`
4. `DS-08`
5. `DS-01`

Hard stop rule:

- if the subset evidence cannot plausibly recover the remaining `2.3350685966624467` budget after the DS-01 plus DS-05 ceiling, do not spend a full E1 rerun

Done when:

- the next benchmark spend is justified by measured subset evidence rather than hope

## What Remains Blocked After This Slice

- `mean CR >= 5.0x` is still not established
- `PT-6 >= 7/8` is still not established
- blind-clone and cold-wheel evidence are still open
- stale status surfaces still need Phase 4 reconciliation, but only after the authority metric path is settled

## Next Best Task

Implement `validation/benchmarks/phase2_gap_budget.py` and `validation/benchmarks/phase2_overhead_decomposition.py`, then use those outputs to write `proofs/artifacts/PHASE2_CANDIDATE_SHORTLIST_20260320.md`.
