# Release Checklist

Date: 2026-03-09
Scope: current private-stage repo truth only

## Current Managed Gate Snapshot

Source of truth:

- `validation/results/release_preflight_report_20260309T040302.json`
- `proofs/FINAL_STATUS.md`

Current verdict:

- release ready: `NO`
- private staging allowed: `YES`
- public publish allowed: `NO`

## Build And Validation Gates

- [x] `cargo test --release`
- [x] `cargo clippy -- -D warnings`
- [x] `python -m pytest -q` with coverage >= 85%
- [x] strict DT run passes with mandatory `SKIPPED=0`
- [x] benchmark split artifacts regenerated (`E0/E1/E2`)
- [x] security scan artifact generated with high/critical = 0
- [ ] SBOM + license manifest + release manifest regenerated cleanly

## Package And Install Gates

- [x] `python -m build ./python`
- [x] fresh-venv smoke artifact exists
- [ ] installed `zpe-iot` console-script smoke re-adjudicated cleanly in managed preflight
  - local note: standalone CLI smoke passed again after editable reinstall on 2026-03-09
- [x] `python -m zpe_iot.cli chemosense-smoke --json`
- [x] chemosense contract tests pass
- [x] chemosense perf profile artifact generated
- [x] chemosense benchmark summary artifact generated
- [x] chemosense provenance manifest verified

## Release Bundle Surface

- [x] `release/RC_20260309T060913/` exists
- [x] bundle manifest hash file exists
- [x] operator mirror docs remain under `project_docs/`

## Known Blocking Checks

- `C07_SBOM_RELEASE_MANIFEST`
  - blocker: `cyclonedx-py` exits `126` in the current managed preflight
- `C10_CHEMOSENSE_CLI_SMOKE`
  - blocker in last managed preflight: installed console-script wrapper pointed at a stale absolute Python path
  - current local note: wrapper was normalized by editable reinstall and standalone CLI smoke now passes, but the full managed preflight has not been rerun

## Deferred Until Explicit Owner Approval

- [ ] git tag push
- [ ] PyPI publication
- [ ] crates.io publication
- [ ] public outreach

## Preflight Command

```bash
bash scripts/release_preflight.sh
```
