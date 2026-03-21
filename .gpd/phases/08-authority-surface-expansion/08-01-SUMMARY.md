# Phase 8 Plan 08-01 Summary

Date: 2026-03-21
Status: mixed

## What This Plan Did

- removed the benchmark/provenance hardcoding that limited the authority surface to `DS-01..DS-08`
- extended dataset build tooling to support `DS-09..DS-12`
- added three executable real-public datasets:
  - `DS-09` CWRU Bearing Drive End 48kHz
  - `DS-10` UCI HAR `body_acc_x` test split
  - `DS-12` UCI Electricity Load Diagrams `MT_001`
- recorded `DS-11` as an explicit blocked source because the named Telemanom no-login path is no longer viable
- reran the widened E1 benchmark on the ready-set only

## Outcome

Phase 8 did not fully close on the exact briefed target, but it did produce a real widened benchmark surface and a concrete blocker.

- `validation/results/bench_summary_E1_real_public_20260321T185546.json` reports `10/11` wins and `mean CR 17.163613932777356x` on the executable ready-set
- `validation/datasets/verify_provenance.py --allow-blocked` now verifies the widened manifest honestly as `11 PASS` and `1 BLOCKED`
- the exact `12 no-login real-public datasets` target remains open because `DS-11` is not currently viable without abandoning the no-login rule
- `DS-12` is a real structural loss on the selected deterministic extraction rule, and an aggregate-load alternative was not adopted because it failed the fidelity floor under quick preset checks

## Immediate Next Step

Carry the widened `11 READY + 1 BLOCKED` authority surface forward without narrating it as a full Phase 8 close, then wire the canonical Comet and Opik benchmark adapters against that honest surface.

```yaml
gpd_return:
  status: completed
  files_written:
    - .gpd/phases/08-authority-surface-expansion/08-01-SUMMARY.md
    - proofs/artifacts/PHASE8_DATASET_EXPANSION_20260321.md
    - validation/datasets/download_datasets.py
    - validation/datasets/manifest.json
    - validation/datasets/verify_provenance.py
    - validation/benchmarks/_common.py
    - validation/benchmarks/run_benchmarks.py
    - validation/benchmarks/generate_report.py
    - validation/results/bench_summary_E1_real_public_20260321T185546.json
  issues:
    - DS-11 named no-login source is not currently viable and is explicitly blocked
    - DS-12 is a real competitor win on the deterministic `MT_001` extraction rule
  next_actions:
    - locate the canonical Comet and Opik project constants from the founding pattern and wire both benchmark adapters with local fallback
    - keep DS-11 blocked until a ratified no-login replacement rule exists
    - do not promote the widened surface as a 12-dataset close while DS-11 remains blocked
```
