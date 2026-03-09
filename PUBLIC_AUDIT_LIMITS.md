# Public Audit Limits

This repo is being staged to a private GitHub repo first.

There is no valid public-release claim yet.

## What The Current Staged Repo Can Establish

- the current repo boundary and source layout
- the current Rust, Python, DT, and benchmark surfaces that exist locally
- the current IMC compatibility pin
- the current managed preflight blockers

## What It Cannot Yet Establish

- public PyPI or crates.io availability
- blind-clone verification
- final release readiness
- clean SBOM and release-manifest regeneration in the current managed environment

## Current Honesty Constraints

- `validation/results/IOT_WAVE1_RELEASE_READINESS_REPORT.md` is historical and contradicted by the newer March 9 preflight failure.
- some historical runbooks, release bundles, and generated artifacts still contain machine-absolute paths
- `project_docs/` is an operator mirror, not the repo front door
- suite linkage is contract-based for private staging, not runtime-coupled to IMC

## Reading Rules

- read `proofs/FINAL_STATUS.md` as the current staged-repo verdict
- read `validation/results/release_preflight_report_20260309T040302.json` as the latest managed gate truth
- read older `validation/results/*readiness*` and `release/RC_*` surfaces as lineage, not as current release authority
