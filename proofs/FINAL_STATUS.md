<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# Final Status

Date: 2026-03-21
Repo stage: private GitHub staging repo

<p>
  <img src="../.github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

- private staging: `engineering verification passed for private-stage use`
- managed release gate: `PASS (17 PASS / 0 FAIL / 1 DEFERRED)`
- public package publication: `owner-deferred by policy`

<p>
  <img src="../.github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

| Surface | Current state | Evidence |
|---|---|---|
| Technical alignment | `PASS` | [Technical alignment proof](artifacts/REPO_TECHNICAL_ALIGNMENT_20260321.md) |
| Managed preflight | `17 PASS / 0 FAIL / 1 DEFERRED` | [Preflight report](../validation/results/release_preflight_report_20260321T205127.json) |
| Strict DT | `27/27 PASS` | [DT report](../validation/results/dt_results_20260321T225304.json) |
| E1 real-public benchmark | `10/11 wins`, `17.16x` mean CR | [E1 summary](../validation/results/bench_summary_E1_real_public_20260321T225305.json) |
| Native wheel cold install | `PASS` on local arm64 macOS path | [Cold-install smoke](../validation/results/fresh_env_smoke_20260321T205515/smoke.log) |
| Current release bundle inventory | `present` | [Bundle manifest](../release/RC_20260321T225526/bundle_manifest.json) |

<p>
  <img src="../.github/assets/readme/section-bars/open-risks-non-blocking.svg" alt="OPEN RISKS (NON-BLOCKING)" width="100%">
</p>

- The only managed-preflight defer is `D01_DEFERRED_PUBLISH`, which means public tag and index publication still require explicit owner ratification.
- `DS-11` remains explicitly blocked and outside the active E1 benchmark surface.
- `DS-12` is a competitor win on the current E1 surface; the repo does not claim universal compressor dominance.
- Public package-index publication is still not claimed.

<p>
  <img src="../.github/assets/readme/section-bars/what-this-directory-is-not.svg" alt="WHAT THIS DIRECTORY IS NOT" width="100%">
</p>

- `validation/results/IOT_WAVE1_RELEASE_READINESS_REPORT.md`
- March 9 release-blocked front-door docs and preflight references
- older `release/RC_*` bundles and operator runbooks under `project_docs/`

<p>
  <img src="../.github/assets/readme/section-bars/where-to-go.svg" alt="WHERE TO GO" width="100%">
</p>

- For proof routing: `PROOF_INDEX.md`
- For replay instructions: `../AUDITOR_PLAYBOOK.md`
- For benchmark depth: `../docs/BENCHMARKS.md`

<p>
  <img src="../.github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>
