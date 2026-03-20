# Plan 01-02 Summary

## Result

- Implemented the compact loss harness at `validation/benchmarks/phase1_loss_scan.py`.
- Ran it and wrote `proofs/artifacts/LOSS_DIAGNOSIS_COMPACT.json`.
- Wrote the bounded diagnosis at `proofs/artifacts/LOSS_DIAGNOSIS.md`.

## Key Findings

- The harness replays the March 20 authority rows for `DS-01` and `DS-05` exactly enough to trust its diagnostics.
- `DS-01` is not a simple threshold miss inside the current fidelity regime. Higher CR is available only by moving to much worse fidelity.
- `DS-05` is already on the best current preset and only moves marginally under threshold sweep, which points to a more structural gap against the byte compressors.
- `WI-1` and `ZH-1` remain real candidates only if their `DT-10` and `DT-11` regressions are repaired.

## Durable Outputs

- `validation/benchmarks/phase1_loss_scan.py`
- `proofs/artifacts/LOSS_DIAGNOSIS_COMPACT.json`
- `proofs/artifacts/LOSS_DIAGNOSIS.md`

## Carry-Forward

- Phase 2 should start from the compact loss scan rather than rediscovering DS-01 and DS-05 behavior.
- Preset-only tuning should not be treated as the main expected lever.

```yaml
gpd_return:
  status: completed
  files_written:
    - validation/benchmarks/phase1_loss_scan.py
    - proofs/artifacts/LOSS_DIAGNOSIS_COMPACT.json
    - proofs/artifacts/LOSS_DIAGNOSIS.md
    - .gpd/phases/01-authority-baseline-reconciliation-and-diagnostic-harness/01-02-SUMMARY.md
  issues: []
  next_actions:
    - $gpd-plan-phase 2 --skip-research
    - Review proofs/artifacts/LOSS_DIAGNOSIS.md before Phase 2 uplift work
```
