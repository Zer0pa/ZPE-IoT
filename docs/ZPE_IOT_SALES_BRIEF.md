<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# ZPE-IoT: Sensor Compression Brief (E1)

<p>
  <img src="../.github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

## What This Brief Is

This is an internal, truth-routed commercial brief. It should be read alongside [BENCHMARKS.md](BENCHMARKS.md), [LEGAL_BOUNDARIES.md](LEGAL_BOUNDARIES.md), and [../proofs/FINAL_STATUS.md](../proofs/FINAL_STATUS.md).

## The Problem

Networked sensors pay for payload size, not for elegance. Any credible wedge here depends on measured byte reduction on real-public data, not on storytelling about embedded intent.

## Proven Results

| Field | Current truth |
|---|---|
| Evidence class | `E1` real-public |
| Active benchmark surface | `DS-01..DS-10`, `DS-12` |
| Current result | `10/11` wins, `17.163613932777356x` mean CR |
| Competitor win still present | `DS-12` |
| Publication posture | Private-stage only; no public package-index claim |
| Installable proof path | Local arm64 macOS native wheel cold-install is evidenced |

See [BENCHMARKS.md](BENCHMARKS.md) for the dataset table and [../validation/results/bench_summary_E1_real_public_20260321T225305.json](../validation/results/bench_summary_E1_real_public_20260321T225305.json) for the raw benchmark authority artifact.

## Boundary Honesty

- This repo does not claim universal dominance. `DS-12` is a competitor win on the promoted surface.
- This repo does not claim public PyPI or crates.io availability.
- This repo does not claim customer or production outcomes beyond the cited repo artifacts.
- Embedded deployment is an engineering direction, not a public release claim in this repo.

## Evaluation Route

1. Use a private repo checkout or owner-shared wheel.
2. Run the current benchmark or a side-by-side comparison on your own telemetry.
3. Compare payload reduction, reconstruction error, and operational constraints against your own baseline.

## Next Step
Run a side-by-side trial on your own telemetry:
`python scripts/customer_demo.py <your_data.csv> --preset <preset>`

<p>
  <img src="../.github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>
