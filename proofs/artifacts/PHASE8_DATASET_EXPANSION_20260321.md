# Phase 8 Dataset Expansion

Date: 2026-03-21

## Scope

Phase 8 widened the real-public authority surface beyond the original `DS-01..DS-08` benchmark contract, but it did not close the exact `12 no-login datasets` target from the brief.

## What Ran

- extended dataset build and provenance tooling from the hardcoded `DS-01..DS-08` path to the dynamic `DS-01..DS-12` path
- rebuilt the dataset manifest with three new executable real-public datasets:
  - `DS-09`: CWRU Bearing Drive End 48kHz (`109.mat`)
  - `DS-10`: UCI HAR `body_acc_x` test split
  - `DS-12`: UCI Electricity Load Diagrams `MT_001`
- recorded `DS-11` as an explicit blocked source because the named Telemanom no-login path is no longer publicly accessible
- reran the E1 benchmark on the executable ready-set only

## Source Viability

### Ready real-public additions

- `DS-09`: direct Case Western Reserve University bearing file downloaded successfully
- `DS-10`: direct UCI HAR archive downloaded successfully
- `DS-12`: direct UCI Electricity Load archive downloaded successfully

### Blocked named source

`DS-11` is blocked on source viability, not on local code:

- the named raw GitHub URL for `P-1.npy` returns `404`
- the historical Telemanom `data.zip` S3 bundle returns `403`
- the upstream Telemanom README now points users to a Kaggle download, which violates the no-login rule for this phase

The repo therefore records `DS-11` as `status=BLOCKED` instead of silently substituting a softer source.

## Provenance Verification

- `validation/datasets/verify_provenance.py --min-class real_public --allow-blocked`:
  - `11 PASS`
  - `1 BLOCKED` (`DS-11`)
- strict verification without `--allow-blocked` fails exactly on `DS-11`, as intended

## Benchmark Result On The Executable Surface

Artifact: `validation/results/bench_summary_E1_real_public_20260321T185546.json`

- executable E1 surface size: `11`
- wins: `10/11`
- mean CR: `17.163613932777356x`

Dataset verdicts:

- `DS-09`: win, `6.380880412591241x`
- `DS-10`: win, `7.4701938344227035x`
- `DS-12`: competitor win, `zpe_iot 120.47058823529412x` vs `zstd 5957.818181818182x`

## DS-12 Integrity Note

The deterministic `MT_001` extraction rule produced a sparse but legitimate meter trace. It is not a ZPE-IoT win.

I also checked a principled aggregate-load alternative before changing the dataset definition. That aggregate signal is more representative, but under the current codec/preset surface it produced inadmissible fidelity (`NRMSE ~ 0.44`) across tested preset families, so no substitution was made. The repo keeps the deterministic `MT_001` extraction and records the loss honestly.

## Verdict

Phase 8 produced a stronger executable authority surface, but it did not close the exact briefed target:

- widened executable real-public surface: achieved
- exact `12 no-login datasets`: not achieved
- blocker is explicit and repo-local, not narrative
