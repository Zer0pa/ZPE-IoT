# IOT Wave-1 Release Readiness Report

Original wave rehearsal date (UTC): 2026-02-20T18:18:45Z
Authority sync date (UTC): 2026-03-21T22:53:05Z
Repo: <REPO_ROOT>

## IMC Freeze Validation
- IMC contract version consumed: `wave1.0`
- IMC vector sha256 consumed: `9c8b905f6c1d30d057955aa9adf0f7ff9139853494dca673e5fbe69f24fba10e`
- Pin check result: PASS
- Canonical coordination metric authority: IMC compatibility vector (`canonical_demo_metrics.total_words=844`)

## Current Authority Anchors
- Managed preflight: <REPO_ROOT>/validation/results/release_preflight_report_20260321T205127.json
- Strict destructive tests: <REPO_ROOT>/validation/results/dt_results_20260321T225304.json
- Real-public benchmark surface: <REPO_ROOT>/validation/results/bench_summary_E1_real_public_20260321T225305.json
- Cold-install proof: <REPO_ROOT>/validation/results/fresh_env_smoke_20260321T205515/smoke.log
- Release manifest: <REPO_ROOT>/validation/results/release_manifest_20260321T205457.json
- License manifest: <REPO_ROOT>/validation/results/license_manifest_20260321T205457.json
- SBOM surfaces: <REPO_ROOT>/validation/results/sbom_20260321T205457.json and <REPO_ROOT>/validation/results/sbom_python_20260321T205457.json

## Historical Wave Ledger
- Phase 0..6 runbooks under `<REPO_ROOT>/validation/runbooks/` remain operator lineage from the February rehearsal.
- Output paths inside those runbooks are historical capture points, not the front-door authority surface used by the current README and docs.

## Managed Gate Summary
Source: <REPO_ROOT>/validation/results/release_preflight_report_20260321T205127.json
- total checks: 18
- pass: 17
- fail: 0
- critical_failures: 0
- deferred only: `D01_DEFERRED_PUBLISH`

## Strict DT Evidence Snapshot
Source: <REPO_ROOT>/validation/results/dt_results_20260321T225304.json
- Strict mode: true
- Result count: 27
- Summary: PASS=27, FAIL=0, SKIPPED=0, BLOCKED=0, NOT_IMPLEMENTED=0, TIMEOUT=0

## Benchmark Authority Snapshot
Source: <REPO_ROOT>/validation/results/bench_summary_E1_real_public_20260321T225305.json
- Headline surface: `6.65×` mean compression across `DS-01..DS-10`
- Current real-public scoreline: `10/11` wins across 11 READY datasets
- Honest outlier: `DS-12` is a real competitor win and stays disclosed
- Honest blocker: `DS-11` remains blocked on source availability

## Publication and Family Boundaries
- PyPI package `zpe-iot==0.1.0` is live.
- Local arm64 macOS cold-install proof is committed and cited above.
- Broader multi-platform wheel closure and outreach remain owner-controlled.
- IMC alignment is documentary and contractual, not runtime repo coupling.

## Unresolved Blockers / Risks
- No unresolved internal gate failures remain on the March authority surface.
- Broader distribution closure beyond the current PyPI package and cited local cold-install proof remains outside this repo's current authority surface.

## Final Readiness Decision
- Useful now, improving continuously.
- Rationale: the current March proof surface closes managed preflight, strict DT, benchmark disclosure, and cold-install validation without internal blockers.
