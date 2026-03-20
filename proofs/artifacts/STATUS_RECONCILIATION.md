# Status Reconciliation

Date: 2026-03-20
Phase: 01 authority baseline reconciliation

## Purpose

Freeze the live March 20 authority surface into one compact artifact and identify the principal repo surfaces that still contradict it.

This is not a repo-wide doc rewrite and it is not a release-ready verdict.

## Live Authority Baseline

### Release authority

Canonical artifacts:

- `validation/results/release_preflight_report_20260320T154022.json`
- `validation/results/dt_results_20260320T174518.json`

Current authoritative state:

- managed preflight: `17 PASS`, `0 FAIL`, `1 DEFERRED`, `0 critical failures`
- only non-pass item: `D01_DEFERRED_PUBLISH`
- strict DT: `27/27 PASS`
- `mandatory_failures: []`

Important correction versus March 9:

- `C07_SBOM_RELEASE_MANIFEST` is now `PASS`
- `C10_CHEMOSENSE_CLI_SMOKE` is now `PASS`
- the March 9 preflight is lineage, not current release authority

### Benchmark authority

Canonical artifact:

- `validation/results/bench_summary_E1_real_public_20260320T174720.json`

Current authoritative state:

- mean E1 compression ratio: `4.369104600542837x`
- PT-6: `PASS` at `6/8`
- current losses: `DS-01`, `DS-05`

Implication:

- release hardening materially improved on March 20
- the governing benchmark wedge target is still not met

## Front-Door Contradiction Inventory

| Surface | Current claim or pointer | Status | Why it conflicts with March 20 authority | Required follow-up |
| ----- | ----- | ----- | ----- | ----- |
| `proofs/FINAL_STATUS.md` | `Date: 2026-03-09`; `release readiness: BLOCKED` | Stale authority surface | Still presents March 9 blocked readiness as current truth after March 20 preflight and DT closure | Replace or supersede with March 20-aware status wording |
| `PUBLIC_AUDIT_LIMITS.md` | instructs readers to use `validation/results/release_preflight_report_20260309T040302.json` as latest managed gate truth | Stale routing surface | Explicitly routes readers to the wrong preflight artifact | Update routing to March 20 authority pair |
| `README.md` | `Latest local managed evidence on 2026-03-09`; `full release preflight: FAIL`; benchmark artifact pinned to March 9 | Stale front door | Entry-point doc still tells new readers the repo is in the older blocked state | Reconcile to March 20 while preserving the open benchmark shortfall |
| `proofs/RELEASE_READINESS_REPORT.md` | `Date: 2026-03-09`; blockers still listed as `C07` and `C10` | Stale release summary | Repeats blockers that are now closed in managed preflight | Replace with March 20-aware summary or archive as lineage |
| `proofs/PROOF_INDEX.md` | `Latest Managed Gate Truth` points at March 9 preflight and March 9 benchmark/DT outputs | Stale proof router | Routes proof review toward superseded artifacts | Point proof routing to March 20 authority artifacts |
| `docs/RELEASE_CHECKLIST.md` | March 9 source-of-truth and unresolved `C07` / `C10` | Stale operator checklist | Checklist still encodes blocked preflight status that no longer matches managed truth | Refresh checklist to separate closed gates from deferred publish |
| `docs/TEST_MATRIX.md` | `Date: 2026-03-09`; says full release preflight still blocked by `C07` and `C10` | Stale validation summary | Test matrix lags the current managed rerun | Refresh matrix date and current gap note |
| `docs/ZPE_IOT_SALES_BRIEF.md` | pins E1 artifact to March 9 | Benchmark-lineage stale | The numeric benchmark headline is still current, but the cited artifact path is stale | Repoint to March 20 benchmark artifact once the doc set is updated |

## Surfaces That Are Lineage, Not Authority

These remain useful as historical lineage but should not drive current status decisions:

- `validation/results/release_preflight_report_20260309T040302.json`
- `validation/results/bench_summary_E1_real_public_20260309T060843.json`
- March 9 status summaries under `proofs/` and `docs/`
- older `release/RC_*` bundles and mirrored operator docs that still embed March 9 routing

## What This Artifact Does Not Claim

- It does not claim public publication is cleared.
- It does not claim blind-clone or cold-wheel evidence is closed.
- It does not claim a commercial wedge is already earned.
- It does not treat `6/8` and `4.3691x` as sufficient to close the benchmark gate.

## Phase 1 Position After Reconciliation

The truthful current state is:

1. March 20 release authority is materially better than the stale March 9 repo narrative.
2. The benchmark authority surface is still short of the desired wedge threshold.
3. The next disciplined step is DS-01 / DS-05 loss diagnosis on the unchanged E1 surface, not doc-polish-as-progress.
