# Releasing

Date: 2026-03-21
Scope: current private-stage repo truth only

## Current State

| Surface | Status |
|---|---|
| Private repo staging | `ALLOWED` |
| Managed preflight | `17 PASS / 0 FAIL / 1 DEFERRED` |
| Public package publication | `DEFERRED BY POLICY` |
| Latest bundle | `release/RC_20260321T225526/` |

The only non-pass in the current managed preflight is `D01_DEFERRED_PUBLISH`, which remains owner-controlled.

## Current Authority Files

- `proofs/FINAL_STATUS.md`
- `proofs/PROOF_INDEX.md`
- `validation/results/release_preflight_report_20260321T205127.json`
- `validation/results/dt_results_20260321T225304.json`

## Private Staging Flow

1. Keep the canonical boundary at the inner repo root.
2. Keep proof and operator surfaces intact.
3. Push scoped changes to the private GitHub repo without force.
4. Regenerate release artifacts when code or docs change the declared truth surface.

## What This File Does Not Claim

- public PyPI availability
- public crates.io availability
- live multi-platform wheel publication
- benchmark scope beyond the active March 21 E1 surface

## Public Publication Prerequisites

Do not publish until all of the following are true:

- explicit owner ratification is given
- current front-door docs and private GitHub render match the authority artifacts
- publication credentials are available for the target package indexes
- any publication-specific wheel or sdist workflow has been executed for the intended targets
