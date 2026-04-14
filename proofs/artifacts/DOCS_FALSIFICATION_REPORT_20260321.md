# Docs Falsification Report

Date: 2026-03-22
Repo: `<REPO_ROOT>`

## Unsupported Claims Removed Or Downgraded

- Fixed the cold-start clone path so the documented install flow no longer fails on case-sensitive filesystems.
- Replaced stale March 9 and intermediate March 21 benchmark promotions in `README.md`, `docs/FAQ.md`, `docs/BENCHMARKS.md`, `docs/ZPE_IOT_SALES_BRIEF.md`, `docs/OUTREACH_TEMPLATE.md`, `proofs/RELEASE_READINESS_REPORT.md`, and `proofs/team_assessment_packet_20260321/*` with the promoted March 21 authority surface (`10/11`, `17.163613932777356x`).
- Removed stale pure-Python wheel language from the active proof/documentation surface and routed native-wheel claims to the verified local arm64 macOS evidence.
- Demoted `docs/ARCH_TIGHTNESS_AUDIT.md` and `docs/ZPE_IOT_SALES_BRIEF.md` from “current” to historical/operator treatment inside `docs/DOC_REGISTRY.md`.
- Removed machine-absolute family references from `docs/family/IOT_IMC_ALIGNMENT_REPORT.md` and `docs/family/IOT_COMPATIBILITY_VECTOR.json`.

## Path And Render Issues Found

- The promoted docs surface was split between styled and plain-text pages. The active root/docs/proofs/family pages now carry the same top-and-tail masthead treatment, and the current engineering references promoted from the docs index now carry the same visual contract.
- `docs/README.md` duplicated proof-routing work that belongs in `proofs/PROOF_INDEX.md`; it now routes instead of duplicating the proof inventory.
- `docs/BENCHMARKS.md` previously used unexplained benchmark shorthand and mixed promoted and placeholder artifacts. It now defines the benchmark terms, separates promoted authority from generated-but-non-promoted outputs, and narrows the dataset table for GitHub scan speed.
- Local asset-path verification across the promoted doc surface returned `ALL_ASSET_PATHS_OK`.
- `git diff --check` on the scoped docs/proofs surface returned clean.

## Remaining Owner Inputs

- Public package publication, tags, and external outreach remain owner-ratified actions by policy.
- No additional owner input is needed to keep the private repo docs truthful and synchronized.

## Live-Vs-Local Drift Found And Resolved

- The private repo docs surface had drifted from the current March 21 authority surface in the sales brief, outreach template, team assessment packet, and readiness report. Those surfaces were reconciled to the current benchmark, wheel, and release-gate artifacts.
- Legacy rerun folders and older release bundles were reduced during this pass so the promoted docs no longer route through the older packet churn.
