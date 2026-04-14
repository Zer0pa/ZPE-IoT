# ZPE-IoT Docs Alignment Plan

Date: 2026-03-21
Repo: <REPO_ROOT>
Working standard: proofs/runbooks/ZER0PA_REPO_DOCS_PLAYBOOK_CANONICAL_2026-03-21.md

## Objective

Bring the repo documentation surface up to the ZPE-IMC structural standard without importing any ZPE-IMC claims, metrics, or release posture that this repo cannot prove.

## Governing Truth Inputs

- proofs/artifacts/REPO_TECHNICAL_ALIGNMENT_20260321.md
- validation/results/release_preflight_report_20260321T205127.json
- validation/results/dt_results_20260321T225304.json
- validation/results/bench_summary_E1_real_public_20260321T225305.json
- release/RC_20260321T225526/bundle_manifest.json
- validation/results/fresh_env_smoke_20260321T205515/smoke.log

## Execution Steps

1. Copy the shared IMC readme assets into `.github/assets/readme/` for GitHub-safe rendering parity.
2. Rewrite the root authority docs around March 21 truth:
   - README.md
   - proofs/FINAL_STATUS.md
   - proofs/PROOF_INDEX.md
   - AUDITOR_PLAYBOOK.md
   - PUBLIC_AUDIT_LIMITS.md
3. Create the missing support docs and registry surface:
   - docs/DOC_REGISTRY.md
   - docs/FAQ.md
   - docs/SUPPORT.md
   - docs/ARCHITECTURE.md
   - docs/LEGAL_BOUNDARIES.md
4. Update governance and release-routing docs to match the verified repo state:
   - CHANGELOG.md
   - CONTRIBUTING.md
   - SECURITY.md
   - SUPPORT.md
   - GOVERNANCE.md
   - RELEASING.md
   - ROADMAP.md
   - CITATION.cff
   - docs/README.md
   - docs/BENCHMARKS.md
   - docs/RELEASE_CHECKLIST.md
5. Run a falsification pass for unsupported claims, path/render drift, and live-vs-local mismatches.
6. Write a standard work receipt and then assess selective git staging/commit/push for only the scoped docs lane files.

## Boundaries

- Do not convert deferred publication into a public-release claim.
- Keep DS-11 outside the active E1 authority surface.
- Treat March 9 release-blocked docs as historical once superseded.
- Keep main-agent ownership for all edited files; subagents are reviewers only.
