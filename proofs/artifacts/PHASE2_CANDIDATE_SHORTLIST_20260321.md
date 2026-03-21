# Phase 2 Candidate Shortlist

Date: 2026-03-21
Automation: Hourly PRD Closer

## Sovereign Anchors

- `validation/results/bench_summary_E1_real_public_20260320T174720.json`
- `proofs/artifacts/PHASE2_GAP_BUDGET_20260321.json`
- `proofs/artifacts/PHASE2_OVERHEAD_DECOMPOSITION_20260321.json`
- `proofs/artifacts/PHASE2_WORKSTREAM_RECHECK_20260320.md`

## Corrected Blocker

The previous `DS-05` / `DS-02` single-bridge framing is not supported by the March 20 E1 authority artifact.

What the new code-backed outputs prove:

- `DS-02` has `gap_to_5x = 0.9525`, but `comparator_headroom = 0.0`
- the residual budget after the generous `DS-01 + DS-05` loss-only ceiling is still `2.3351`
- no single winning dataset can repay that residual budget alone
- `DS-05`, `DS-02`, and `DS-08` do share a smooth low-entropy payload sink family
- `DS-06` does not share that family, but its `gap_to_5x = 0.9113` is still large enough that Phase 2 cannot ignore it

The single highest-leverage blocker is therefore:

- Phase 2 still lacks a triad-aware subset plan that can test the smooth-series slice honestly while proving early whether the separate `DS-06` deficit makes the wedge path unattainable

## Shortlist

### Candidate A: Smooth-series payload specialization

- Target datasets: `DS-05`, `DS-02`, `DS-08`
- Candidate family: payload-side specialization for smooth low-entropy windows, not wrapper retuning and not fixed-header tinkering
- Why it survives:
  - all three datasets land in the same `smooth_low_entropy_payload` family
  - `DS-05` is the largest current loss
  - `DS-02` and `DS-08` are the two largest winner-side gaps that share the same measured sink class
- DT risk:
  - must preserve `DT-10` monotonicity
  - must not change packet wrappers or native parity surfaces
  - must keep `NRMSE(window-normalized)` inside the current benchmark contract
- Go/no-go:
  - `GO` only if the prototype cuts mean bytes per `256`-sample window on all three target datasets without introducing any monotonic inversions on the authority subset
  - `NO-GO` if the gains are confined to `DS-05` only or require a wrapper stage

### Candidate B: DS-06-specific dynamic-range path

- Target datasets: `DS-06`
- Candidate family: separate high-variance payload path for large-step telemetry
- Why it survives:
  - `DS-06` has `gap_to_5x = 0.9113`
  - decomposition marks it as `high_variance_payload`, not part of the smooth-series cluster
- DT risk:
  - higher risk than Candidate A because any alternate dynamic-range handling can affect fidelity and deterministic packet shape
- Go/no-go:
  - `GO` only after Candidate A proves real subset gains and only if the remaining budget still requires `DS-06`
  - `NO-GO` as a first prototype because it does not help `DS-05`

### Candidate C: Mixed subset verdict and early wedge downgrade

- Target datasets: `DS-05`, `DS-02`, `DS-08`, `DS-06`
- Candidate family: not a codec change, but an execution rule
- Why it survives:
  - the authority math already shows the wedge path needs more than one winner-side recovery source
  - the decomposition already shows that one family will not cover every remaining deficit
- Go/no-go:
  - `GO` if Candidate A leaves a plausible remaining path through `DS-06`
  - `NO-GO` if Candidate A improves the smooth-series slice but the residual budget still depends on a second mechanism with no measured basis

## Concrete Solution Tasks

### Task 1: Build the smooth-series subset probe

Owner files:

- `validation/benchmarks/phase2_smooth_series_probe.py`
- `proofs/artifacts/PHASE2_SMOOTH_SERIES_PROBE_20260321.json`

Required work:

- prototype one monotone payload-side mechanism against `DS-05`, `DS-02`, and `DS-08`
- report baseline vs candidate bytes per `256`-sample window
- run the authority-subset monotonicity check before any full E1 rerun

Hard stop:

- stop immediately if any target dataset regresses on monotonicity or if only `DS-05` moves materially

### Task 2: Recompute the residual budget after the smooth-series slice

Owner files:

- `proofs/artifacts/PHASE2_SMOOTH_SERIES_PROBE_20260321.json`
- `proofs/artifacts/PHASE2_GAP_BUDGET_20260321.json`

Required work:

- convert the subset gains into updated total-CR budget math
- decide whether `DS-06` is still mandatory for any plausible `>= 5.0x` path

Hard stop:

- if the updated residual still requires a second unproven mechanism with no measured path, downgrade the wedge path instead of widening the search

### Task 3: Spend a DS-06 probe only if Task 2 leaves a live path

Owner files:

- `validation/benchmarks/phase2_high_variance_probe.py`
- `proofs/artifacts/PHASE2_HIGH_VARIANCE_PROBE_20260321.json`

Required work:

- only after Task 2 passes, test one DS-06-specific path on the high-variance subset
- keep the proving surface small and explicit

Hard stop:

- no full E1 rerun unless the combined subset evidence still supports both `mean CR >= 5.0x` and `PT-6 >= 7/8` without a DT-regression expectation

## Rejected Directions

- `DS-02`-alone bridge narratives
- WI-1 / ZH-1 wrapper retuning
- `DS-01`-only tuning stories
- full E1 reruns before subset evidence closes the corrected bridge math
