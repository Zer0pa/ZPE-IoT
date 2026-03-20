# Phase 01 Research

## Phase

- `01` Authority Baseline Reconciliation And Diagnostic Harness
- Research date: `2026-03-20`
- Contract slice: freeze the real March 20 authority baseline, diagnose `DS-01` and `DS-05`, and carry forward only those uplift paths that remain truthful under strict gates.

## Authority Anchors

Read order for this phase:

1. `validation/results/release_preflight_report_20260320T154022.json`
2. `validation/results/dt_results_20260320T174518.json`
3. `validation/results/bench_summary_E1_real_public_20260320T174720.json`
4. `proofs/artifacts/WAVE2_GPD_BRIEF_20260320.md`
5. `proofs/FINAL_STATUS.md`
6. `PUBLIC_AUDIT_LIMITS.md`
7. `/Users/Zer0pa/ZPE/ZPE IoT/team_status_packet_2026-03-20/00_STATUS_AND_AUGMENTATION_SUMMARY.md`
8. `/Users/Zer0pa/ZPE/ZPE IoT/.gpd/research-map/CONCERNS.md`

## Established March 20 Baseline

### Release authority

- Managed preflight now reports `17 PASS`, `0 FAIL`, `1 DEFERRED`, `0 critical_failures`, with only `D01_DEFERRED_PUBLISH` still deferred.
- The previously blocking checks `C07_SBOM_RELEASE_MANIFEST` and `C10_CHEMOSENSE_CLI_SMOKE` are both `PASS` in the March 20 authority artifact.
- Strict DT reports `27/27 PASS` and `mandatory_failures: []`.

### Benchmark authority

- The governing benchmark surface remains `validation/results/bench_summary_E1_real_public_20260320T174720.json`.
- Mean E1 compression ratio is `4.369104600542837x`.
- PT-6 is `PASS` at `6/8`.
- The only current losses are `DS-01` and `DS-05`.

### Immediate implication

- March 9 blocker narratives are stale as release authority.
- The project still does not earn an unqualified commercial wedge because the governing benchmark target remains unmet.
- Phase 1 should freeze that truth surface before any uplift or status polish work continues.

## Conflict Surface That Must Be Reconciled

Front-door or operator-facing docs still point at the older March 9 state or benchmark artifact lineage:

- `proofs/FINAL_STATUS.md`
- `PUBLIC_AUDIT_LIMITS.md`
- `README.md`
- `proofs/RELEASE_READINESS_REPORT.md`
- `proofs/PROOF_INDEX.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/TEST_MATRIX.md`
- `docs/OUTREACH_TEMPLATE.md`
- `docs/ZPE_IOT_SALES_BRIEF.md`

Phase 1 should not rewrite the whole repo narrative. It should produce one compact reconciliation artifact that:

- states the live March 20 authority numbers,
- inventories the front-door contradictions,
- distinguishes stale lineage docs from live authority,
- avoids converting the benchmark shortfall into a pass story.

## Benchmark Method Constraints

The Phase 1 diagnosis must stay on the unchanged authority surface implemented in `validation/benchmarks/_common.py`:

- ZPE pathway: `encode(window).to_bytes()` then `decode(packet)`
- comparator pathway: compress raw float64 bytes and decompress raw float64 bytes
- benchmark truncation: first `256 * 64` samples per dataset
- windowing: `256` samples per window
- fidelity metric: `NRMSE(window-normalized)`
- dataset presets:
  - `DS-01 -> generic`
  - `DS-05 -> pressure`

Those are not incidental details. Any diagnosis that ignores them risks explaining the wrong benchmark.

## DS-01 And DS-05 Findings

### Dataset provenance

- `DS-01`: UCI AirQuality CO channel with sentinel `-200` rows removed.
- `DS-05`: NOAA hourly temperature channel, with the trace cycled `2x` to satisfy the minimum `4096`-sample floor.

### Authority losses on March 20 surface

- `DS-01`
  - ZPE-IoT: `3.9873890008950217x`
  - best baseline: `zlib 4.261137440758294x`
  - gap: about `0.274x`
- `DS-05`
  - ZPE-IoT: `4.582866611384806x`
  - best baseline: `zlib 7.021212770516391x`
  - gap: about `2.438x`

### Compact preset scan signal

Using the repo venv and the same benchmark windowing:

- `DS-01`
  - `generic`, `temperature`, `flow`, and `gps_track` all land near `3.987x` at the current fidelity.
  - `vibration`, `accelerometer`, `voltage`, and `current` can exceed `11.66x`, but only by driving `NRMSE(window-normalized)` to about `0.2205`, which is a materially different fidelity regime.
  - Threshold sweep on `generic` is effectively flat from `0.001` through `0.5`, so the current loss does not look like a simple threshold miss.
- `DS-05`
  - `pressure` is already the best preset in the current catalog at about `4.583x`.
  - Threshold sweep on `pressure` is flat through `0.1` and reaches only about `4.674x` at `0.5`, with worse fidelity.
  - This points away from simple preset mismatch and toward a more structural gap against the byte compressors on this trace.

### Structure signal

- `DS-01`
  - `unique_ratio ~= 0.116`
  - `zero_diff_ratio ~= 0.0067`
  - `35/35` windows are unique
  - interpretation: irregular, non-repeating movement where aggressive preset shifts buy CR only by accepting much larger distortion
- `DS-05`
  - `unique_ratio ~= 0.0334`
  - `zero_diff_ratio ~= 0.2227`
  - very low `large_jumps_gt_1std_ratio ~= 0.00049`
  - interpretation: smooth low-entropy trace with many repeated or near-repeated values, which is favorable to byte compressors and unfavorable to the present ZPE packetization

## Carry-Forward From Prior Uplift Work

Two prior uplift ideas are real and should not be rediscovered from scratch:

- `WI-1` (`validation/results/wi1_ablation_20260220T050410.json`)
  - `mean_cr_gain = 0.5062667882814955`
  - not retained
  - introduces strict failures in `DT-10 Monotonicity` and `DT-11 Cross-Platform Parity`
- `ZH-1` (`validation/results/zh1_ablation_20260219T030327.json`)
  - `mean_cr_gain = 0.08701008813353232`
  - not retained
  - also introduces strict failures in `DT-10` and `DT-11`

Implication:

- Phase 2 should treat `WI-1` and `ZH-1` as known candidates with known gate failures.
- They are not valid wedge evidence unless the monotonicity and parity regressions are explicitly resolved.

## Recommended Phase 1 Execution

### Plan `01-01`

Produce `proofs/artifacts/STATUS_RECONCILIATION.md` that:

- freezes the March 20 release and benchmark truth surface,
- lists the exact stale front-door contradictions,
- separates live authority from lineage docs,
- does not yet rewrite the repo into a public-ready narrative.

### Plan `01-02`

Produce a reusable compact diagnosis harness that:

- scans `DS-01` and `DS-05` across presets,
- reproduces the current mapped-preset authority rows,
- records threshold-sweep evidence for the current mapped presets,
- writes a bounded diagnosis artifact that distinguishes:
  - preset-selection loss,
  - fidelity-regime tradeoff,
  - and likely structural baseline mismatch.

## Disconfirming Observations

These observations would force a rethink:

- A DT-safe, authority-matching diagnostic rerun shows that `DS-05` can move materially toward the best baseline through simple preset or threshold changes alone.
- A compact scan shows that `DS-01` can clear its baseline gap at near-current fidelity without changing the benchmark contract.
- The March 20 preflight or strict DT artifacts are superseded again during this phase.

## Research Verdict

Phase 1 should not chase a narratable win. The disciplined path is:

1. freeze the March 20 authority baseline into a compact reconciliation artifact,
2. implement a compact DS-01 / DS-05 scan harness,
3. use that evidence to decide whether Phase 2 is parameter work, algorithm work, or honest wedge narrowing,
4. carry forward `WI-1` and `ZH-1` only as rejected-until-repaired candidates.
