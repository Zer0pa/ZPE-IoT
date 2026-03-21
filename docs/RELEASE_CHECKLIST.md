<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# Release Checklist

Date: 2026-03-21
Scope: current private-stage repo truth only

<p>
  <img src="../.github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

| Field | Current truth |
|---|---|
| Managed preflight | `17 PASS / 0 FAIL / 1 DEFERRED` |
| Private staging | `engineering verification passed for private-stage use` |
| Public publish | `owner-deferred pending explicit approval` |
| Source of truth | `../validation/results/release_preflight_report_20260321T205127.json`, `../proofs/FINAL_STATUS.md` |

<p>
  <img src="../.github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

## Build And Validation Gates

- [x] `cargo test --release`
- [x] `cargo clippy -- -D warnings`
- [x] `python -m pytest -q` with coverage >= 85%
- [x] strict DT run passes with mandatory `SKIPPED=0`
- [x] benchmark split artifacts regenerated (`E0/E1/E2`)
- [x] security scan artifact generated with high/critical = 0
- [x] SBOM + license manifest + release manifest regenerated cleanly

## Package And Install Gates

- [x] `python -m build ./python`
- [x] fresh-venv smoke artifact exists
- [x] installed `zpe-iot` console-script smoke passes in managed preflight
- [x] `python -m zpe_iot.cli chemosense-smoke --json`
- [x] chemosense contract tests pass
- [x] chemosense perf profile artifact generated
- [x] chemosense benchmark summary artifact generated
- [x] chemosense provenance manifest verified
- [x] local arm64 native wheel cold-install smoke is closed

## Release Bundle Surface

- [x] `release/RC_20260321T225526/` exists
- [x] bundle manifest exists
- [x] operator mirror docs remain under `project_docs/`

<p>
  <img src="../.github/assets/readme/section-bars/unreleased.svg" alt="UNRELEASED" width="100%">
</p>

## Deferred Until Explicit Owner Approval

- [ ] git tag push
- [ ] PyPI publication
- [ ] crates.io publication
- [ ] public outreach

The only deferred managed-preflight check is `D01_DEFERRED_PUBLISH`.

## Current Non-Publish Boundaries

- `DS-11` remains outside the active E1 benchmark authority surface.
- The multi-platform wheel workflow exists, but public publication has not been executed.
- Public package-index availability is not claimed anywhere in this repo.

## Preflight Command

```bash
bash scripts/release_preflight.sh
```

<p>
  <img src="../.github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>
