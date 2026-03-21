<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# Releasing

Date: 2026-03-21
Scope: current private-stage repo truth only

<p>
  <img src=".github/assets/readme/section-bars/release-notes.svg" alt="RELEASE NOTES" width="100%">
</p>

| Surface | Status |
|---|---|
| Private repo staging | `ALLOWED` |
| Managed preflight | `17 PASS / 0 FAIL / 1 DEFERRED` |
| Public package publication | `DEFERRED BY POLICY` |
| Latest bundle | `release/RC_20260321T225526/` |

The only non-pass in the current managed preflight is `D01_DEFERRED_PUBLISH`, which remains owner-controlled.

<p>
  <img src=".github/assets/readme/section-bars/evidence.svg" alt="EVIDENCE" width="100%">
</p>

| Artifact | Purpose |
|---|---|
| `proofs/FINAL_STATUS.md` | Short current verdict |
| `proofs/PROOF_INDEX.md` | Current proof router |
| `validation/results/release_preflight_report_20260321T205127.json` | Managed release-gate truth |
| `validation/results/dt_results_20260321T225304.json` | Strict DT closure |

<p>
  <img src=".github/assets/readme/section-bars/setup-and-verification.svg" alt="SETUP AND VERIFICATION" width="100%">
</p>

1. Keep the canonical boundary at the inner repo root.
2. Keep proof and operator surfaces intact.
3. Push scoped changes to the private GitHub repo without force.
4. Regenerate release artifacts when code or docs change the declared truth surface.

<p>
  <img src=".github/assets/readme/section-bars/no-change-guarantees.svg" alt="NO CHANGE GUARANTEES" width="100%">
</p>

- public PyPI availability
- public crates.io availability
- live multi-platform wheel publication
- benchmark scope beyond the active March 21 E1 surface

<p>
  <img src=".github/assets/readme/section-bars/unreleased.svg" alt="UNRELEASED" width="100%">
</p>

Do not publish until all of the following are true:

- explicit owner ratification is given
- current front-door docs and private GitHub render match the authority artifacts
- publication credentials are available for the target package indexes
- any publication-specific wheel or sdist workflow has been executed for the intended targets

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>
