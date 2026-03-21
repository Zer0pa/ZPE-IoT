# Phase 2 DS-05 / DS-02 Bridge Tasking

Date: 2026-03-20
Phase: 02 targeted compression uplift

## Sovereign Anchors

- `validation/results/release_preflight_report_20260320T154022.json`: `17 PASS`, `0 FAIL`, `1 DEFERRED`, `0 critical failures`
- `validation/results/dt_results_20260320T174518.json`: strict DT authority surface still green
- `validation/results/bench_summary_E1_real_public_20260320T174720.json`: `mean CR 4.369104600542837x`, `PT-6 6/8`

## Single Highest-Leverage Open Blocker

The governing blocker is still the open E1 wedge gate, but the next decisive blocker is now narrower than the generic byte-sink slice:

- Phase 2 does not yet know whether one DT-safe mechanism can improve both `DS-05` and `DS-02`
- that shared-mechanism question is the fastest honest route to `mean CR >= 5.0x`
- without answering it, the project is still measuring a broad subset without proving which pair can actually carry the residual budget

## Why DS-05 Plus DS-02 Dominates Now

The March 20 authority artifact implies these per-dataset comparator gaps:

| Dataset | ZPE-IoT CR | Best current baseline CR | Recoverable headroom |
| ------- | ---------- | ------------------------ | -------------------- |
| `DS-05` | `4.582866611384806x` | `7.021212770516391x` | `2.438346159131585` |
| `DS-02` | `4.047529175635959x` | `6.396794044230139x` | `2.34926486859418` |
| `DS-06` | `4.08866974147015x` | `5.19209287936424x` | `1.10342313789409` |
| `DS-08` | `4.142596930084757x` | `4.712971892514695x` | `0.570374962429938` |
| `DS-01` | `3.9873890008950217x` | `4.261137440758294x` | `0.2737484398632725` |

Already frozen:

- current total CR budget: `34.952836804342696`
- target total CR budget: `40.0`
- missing total CR budget: `5.047163195657304`
- `DS-01` plus `DS-05` ceiling: `4.708116425417193x`
- residual budget after that ceiling: `2.3350685966624454`

The new leverage fact is:

- `DS-02` alone has `2.34926486859418` theoretical headroom
- that is slightly larger than the full residual budget left after `DS-01` plus `DS-05`
- if a DT-safe mechanism can move both `DS-05` and `DS-02` materially, the 5.0x gate stays alive
- if `DS-02` does not share a usable byte-sink structure with `DS-05`, the path to `5.0x` becomes much narrower and should be treated as at-risk early

## Concrete Solution Tasks

### Task 1: Promote DS-02 to first-class bridge target

Update the Phase 2 execution contract so `DS-02` is no longer just one member of a generic subset.

Required result:

- the next uplift pass explicitly treats `DS-05` as the primary loss case and `DS-02` as the primary bridge case
- `DS-06` and `DS-08` remain secondary confirmation datasets
- `DS-01` remains a tail check, not the main budget source

Done when:

- the project can explain why the first serious prototype is judged on `DS-05` plus `DS-02`, not on a diffuse five-dataset tour

### Task 2: Implement a ranked budget artifact in code

Create `validation/benchmarks/phase2_gap_budget.py`.

It must:

- read `validation/results/bench_summary_E1_real_public_20260320T174720.json`
- rank datasets by recoverable headroom
- emit the `DS-01` plus `DS-05` ceiling
- emit the residual budget after that ceiling
- emit the `DS-05 + DS-02 + DS-01` theoretical ceiling of `5.001774533991466x`
- state explicitly that `DS-02` is the only single winning dataset whose current comparator gap exceeds the residual budget

Done when:

- the DS-05 / DS-02 bridge hypothesis is reproducible from code instead of narrative arithmetic

### Task 3: Make overhead decomposition answer the bridge question first

Create `validation/benchmarks/phase2_overhead_decomposition.py`.

The first pass must answer these two questions before anything else:

1. Is `DS-05` primarily limited by fixed packet overhead, payload inefficiency, or missing repeat exploitation?
2. Does `DS-02` expose the same dominant byte sink strongly enough that one mechanism could improve both datasets?

Required outputs:

- per-dataset header share
- payload share
- per-window payload growth
- repeat or zero-delta prevalence when it can be measured cheaply
- a compact `same_sink_family` verdict for `DS-05` vs `DS-02`

Evaluation order:

1. `DS-05`
2. `DS-02`
3. `DS-06`
4. `DS-08`
5. `DS-01`

Done when:

- the project can say whether the most important loss case and the most important bridge case belong to the same candidate family

### Task 4: Gate candidate shortlist creation on the bridge verdict

Create `proofs/artifacts/PHASE2_CANDIDATE_SHORTLIST_20260320.md` only after the decomposition produces a bridge verdict.

Decision rule:

- if `DS-05` and `DS-02` share a plausible DT-safe byte sink, shortlist only candidate families that address both together
- if they do not, record that Phase 2 likely cannot reach `5.0x` without a broader mechanism and downgrade the wedge path accordingly

Reject by default:

- WI-1 or ZH-1 retuning loops
- `DS-01`-only uplift stories
- any candidate that cannot explain where the residual `2.3350685966624454` budget would come from

Done when:

- the next prototype decision is constrained by the bridge verdict rather than by generic optimism

## What Remains Blocked After This Tasking

- `mean CR >= 5.0x` is still unproven
- `PT-6 >= 7/8` is still unproven
- blind-clone verification is still open
- cold-wheel verification is still open
- truthful front-door status-surface reconciliation still belongs to the later closeout phase unless the wedge path is abandoned early

## Next Best Task

Implement `validation/benchmarks/phase2_gap_budget.py` with explicit bridge ranking, then implement `validation/benchmarks/phase2_overhead_decomposition.py` so the first decomposition answers whether `DS-05` and `DS-02` can share a DT-safe uplift mechanism.
