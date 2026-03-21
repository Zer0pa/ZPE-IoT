# Phase 2 Authority-Gap Tasking

Date: 2026-03-20
Phase: 02 targeted compression uplift

## Single Highest-Leverage Open Blocker

The highest-leverage open blocker is no longer release preflight. March 20 authority already closed that surface at `17 PASS`, `0 FAIL`, `1 DEFERRED`, `0 critical failures`.

The real blocker is this:

- the sovereign benchmark gate is still open at `mean CR 4.369104600542837x`
- the target remains `mean CR >= 5.0x`
- `PT-6` remains `6/8`
- Phase 2 does not yet have a viable authority-path plan to recover the missing mean-CR budget honestly

## Why This Blocker Dominates

The March 20 E1 authority artifact contains 8 datasets.

That means:

- current total CR budget = `4.369104600542837 * 8 = 34.952836804342696`
- target total CR budget = `5.0 * 8 = 40.0`
- missing total budget = `5.047163195657304`

If `DS-01` and `DS-05` were each lifted only to the current best baseline level, the gain would be:

- `DS-01`: `4.261137440758294 - 3.9873890008950217 = 0.2737484398632725`
- `DS-05`: `7.021212770516391 - 4.582866611384806 = 2.438346159131585`
- combined gain = `2.7120945989948573`

That would raise the E1 mean only to:

- `4.708116425417193x`

So the blocker is not just "fix the two current losses."

The blocker is:

- Phase 2 still needs about `2.3350685966624467` more total CR points
- that extra budget must come from already-winning datasets or from a new cross-dataset mechanism
- loss-only closure is mathematically insufficient

## Consequence For Execution

The next honest uplift step must target both:

1. `DS-05`, because it is the largest single gap and can also lift `PT-6` to `7/8`
2. cross-dataset overhead reduction on low-margin winners, because the mean-CR target cannot be reached from `DS-01` plus `DS-05` alone

This immediately rules out two bad continuations:

- spending more time on WI-1 or ZH-1 zlib-level retuning after the March 20 monotonicity probe
- treating DS-01 plus DS-05 closure as a complete benchmark plan

## Concrete Solution Tasks

### Task 1: Freeze the authority-gap budget

- Recompute the March 20 mean-CR budget from the authoritative E1 artifact.
- Persist the DS-01 plus DS-05-only ceiling in a durable artifact.
- Carry forward the exact residual budget that still has to come from already-winning datasets.

Done when:

- no Phase 2 work item can claim sufficiency without passing through this budget math

### Task 2: Measure packet byte sinks on the authority subset

Target datasets:

- `DS-05`
- `DS-02`
- `DS-06`
- `DS-08`
- `DS-01`

Measure:

- header and fixed-overhead share
- payload-token share
- repeat or zero-delta structure
- run-length opportunities
- per-window variance versus packet growth

Done when:

- the project has measured reasons for where additional CR can still come from on the authority subset

### Task 3: Shortlist DT-safe candidate families

Only keep candidate families that can plausibly help both `DS-05` and at least one low-margin winner.

Candidate classes to consider:

- packet-overhead reduction
- run-aware secondary packing that preserves monotone size behavior
- smooth-series specialization for low-entropy windows

Reject by default:

- wrapper-level retuning already disproven by `DT-10`
- preset-threshold storytelling already disproven by Phase 1

Done when:

- each candidate has target datasets, expected gain surface, and explicit DT/parity risks

### Task 4: Gate the next prototype before a full E1 rerun

Evaluation order:

1. `DS-05`
2. `DS-02`
3. `DS-06`
4. `DS-08`
5. `DS-01`

Hard stop rule:

- if the prototype cannot plausibly recover enough budget on that subset, do not spend a full E1 rerun on it

Done when:

- the next execution pass is bounded, authority-aligned, and math-backed

## Current Position After Tasking

- March 20 release truth is materially stronger than March 9 lineage.
- The wedge gate is still open.
- The principal benchmark blocker is now a quantified cross-dataset budget problem.
- The next best task is not another generic uplift attempt.
- The next best task is measured byte-sink decomposition plus a DT-safe candidate shortlist for Phase `02-02`.
