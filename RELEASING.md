# Releasing

This file describes the release posture for ZPE-IoT as of 2026-03-09.

## Current State

- private repo staging: in scope
- public release: out of scope
- PyPI publish: blocked
- crates.io publish: blocked

## Current Blocking Checks

- `C07_SBOM_RELEASE_MANIFEST`
- `C10_CHEMOSENSE_CLI_SMOKE`

See `proofs/FINAL_STATUS.md` and `validation/results/release_preflight_report_20260309T040302.json`.

## Private Staging Flow

1. keep the canonical boundary at the inner repo root
2. keep proof and operator surfaces intact
3. push `main` to the private GitHub repo without force
4. stop before blind-clone verification or public release work

## Public Release Prerequisites

Do not publish until all of the following are true:

- managed preflight is green
- blind-clone verification is complete
- current front-door docs do not outrun proof
- suite linkage and central/public truth surfaces are reconciled
