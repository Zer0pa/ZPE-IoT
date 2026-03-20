# Loss Diagnosis

Date: 2026-03-20
Phase: 01 loss diagnosis

## Purpose

Explain the remaining March 20 authority-surface losses without weakening the benchmark contract.

Authority anchor:

- `validation/results/bench_summary_E1_real_public_20260320T174720.json`

New compact evidence:

- `validation/benchmarks/phase1_loss_scan.py`
- `proofs/artifacts/LOSS_DIAGNOSIS_COMPACT.json`

## Method

The compact scan uses the same benchmark discipline as the authority artifact:

- first `256 * 64` samples
- `256`-sample windows
- ZPE path: `encode(window).to_bytes()` then `decode(packet)`
- fidelity metric: `NRMSE(window-normalized)`
- mapped presets:
  - `DS-01 -> generic`
  - `DS-05 -> pressure`

Replay result:

- `DS-01` mapped replay matches the authority row exactly enough to treat the scan as benchmark-faithful.
- `DS-05` mapped replay also matches the authority row exactly enough to treat the scan as benchmark-faithful.

## DS-01

### Authority loss

- ZPE-IoT: `3.9873890008950217x`
- best baseline: `zlib 4.261137440758294x`
- gap: about `0.274x`

### Scan result

- The mapped preset `generic` is effectively tied with `gps_track`, `temperature`, and `flow` at the current fidelity regime.
- Threshold sweep on `generic` is flat from `0.001` through `0.5`.
- Higher-CR presets do exist, but only by moving into a much worse fidelity regime:
  - `vibration` / `accelerometer` / `voltage` / `current` reach about `11.66x`
  - their `NRMSE(window-normalized)` rises to about `0.2205`
  - that is about `76.5x` the mapped-preset error

### Diagnosis

`DS-01` does not look like a simple threshold or mapped-preset mistake inside the current near-authority fidelity regime.

What the scan supports:

- the current generic-style family is already near its local ceiling on this dataset,
- the dataset is irregular and non-repeating enough that large CR gains come only from accepting much larger distortion,
- Phase 2 should not spend time on generic threshold twiddling and call that a real lever.

What remains open:

- a different algorithmic idea could still improve `DS-01`,
- but Phase 1 evidence does not support a claim that current-catalog tuning is sufficient.

## DS-05

### Authority loss

- ZPE-IoT: `4.582866611384806x`
- best baseline: `zlib 7.021212770516391x`
- gap: about `2.438x`

### Scan result

- The mapped preset `pressure` is already the best preset in the current catalog.
- The next-best preset family (`temperature`, `gps_track`, `flow`, `generic`) is worse by about `0.082x`.
- Threshold sweep on `pressure` is flat through `0.1`.
- Raising threshold to `0.2` adds only about `0.0156x`.
- Raising threshold to `0.5` adds only about `0.0915x` while increasing `NRMSE(window-normalized)` by about `32%`.

Signal structure from the compact scan:

- `unique_ratio ~= 0.0334`
- `zero_diff_ratio ~= 0.2227`
- `large_jumps_gt_1std_ratio ~= 0.00049`
- manifest note: the source trace was cycled `2x` to reach the minimum sample floor

### Diagnosis

`DS-05` looks structurally unfavorable to the current packetization relative to the byte compressors.

What the scan supports:

- the current loss is not mainly a preset-catalog miss,
- the current loss is not mainly a mapped-threshold miss,
- the trace has low-entropy, smooth behavior that general-purpose compressors exploit much better than the present ZPE packet format.

What remains open:

- a new algorithmic stage could still change the outcome,
- but the current preset catalog does not get meaningfully close to the best baseline.

## Carry-Forward Constraint For Phase 2

Two prior uplift paths are real, but neither is currently admissible as authority progress:

- `WI-1`
  - mean CR gain: `0.5062667882814955`
  - pushes `DS-01` to about `5.6898x`
  - pushes `DS-05` to about `7.0439x`
  - rejected because it introduces `DT-10 Monotonicity` and `DT-11 Cross-Platform Parity` failures
- `ZH-1`
  - mean CR gain: `0.08701008813353232`
  - pushes `DS-01` only to about `4.0525x`
  - pushes `DS-05` to about `5.1644x`
  - also rejected because it introduces `DT-10` and `DT-11` failures

Phase 2 therefore has only two truthful paths:

1. repair a candidate such as `WI-1` or `ZH-1` so that `DT-10` and `DT-11` remain green, or
2. pursue a new DT-safe uplift idea and accept that wedge narrowing may be the honest outcome if `DS-05` remains structurally weak.

## Verdict

Phase 1 evidence supports the following bounded conclusion:

- `DS-01` is a near-margin loss under the current fidelity regime, but not one that simple threshold tuning fixes.
- `DS-05` is a large structural loss under the current preset catalog.
- The next meaningful uplift work must be algorithmic and DT-aware, not preset-storytelling.
- Until such a path is validated on the unchanged authority surface, the honest wedge story remains conditional rather than closed.
