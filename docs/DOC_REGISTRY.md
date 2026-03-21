<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# Documentation Registry

[README](../README.md) | [Architecture](ARCHITECTURE.md) | [Proofs](../proofs/PROOF_INDEX.md) | [Governance](../GOVERNANCE.md) | [Family](family/IOT_IMC_ALIGNMENT_REPORT.md)

<p>
  <img src="../.github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

This file indexes the active documentation and evidence surface for ZPE-IoT.

Canonical current-status values live in `../README.md` and `../proofs/FINAL_STATUS.md`. This registry maps where deeper concerns live and which files are historical or generated.

<p>
  <img src="../.github/assets/readme/section-bars/proof-corpus.svg" alt="PROOF CORPUS" width="100%">
</p>

| Path | Class | Purpose | Status | Authority level |
|---|---|---|---|---|
| `../README.md` | Front door | Canonical authority block and repo summary | Current | Canonical |
| `../proofs/FINAL_STATUS.md` | Proof | Current verdict and caveats | Current | Canonical |
| `../proofs/PROOF_INDEX.md` | Proof | Current artifact router | Current | Canonical |
| `../AUDITOR_PLAYBOOK.md` | Audit | Shortest honest replay path | Current | Canonical |
| `../PUBLIC_AUDIT_LIMITS.md` | Audit | Public-boundary and inference limits | Current | Canonical |
| `../RELEASING.md` | Release | Release posture and publication boundary | Current | Canonical |
| `../GOVERNANCE.md` | Governance | Evidence and status semantics | Current | Canonical |
| `BENCHMARKS.md` | Benchmark | Current benchmark authority and boundaries | Current | Supporting |
| `ARCHITECTURE.md` | Architecture | Runtime map and package-surface truth | Current | Supporting |
| `README.md` | Navigation | Documentation index and routing layer | Current | Supporting |
| `RELEASE_CHECKLIST.md` | Release | Current checklist and deferred items | Current | Supporting |
| `FAQ.md` | Reader support | Reader-facing questions and boundary answers | Current | Supporting |
| `SUPPORT.md` | Reader support | Support routing and response expectations | Current | Supporting |
| `LEGAL_BOUNDARIES.md` | Legal boundary | Compact license and release-boundary note | Current | Supporting |
| `../CHANGELOG.md` | Release history | Public delta log for this repo surface | Current | Supporting |
| `../CONTRIBUTING.md` | Contribution | Contributor workflow and local gates | Current | Supporting |
| `../SECURITY.md` | Security | Vulnerability reporting path | Current | Supporting |
| `../SUPPORT.md` | Support | Root support policy and contact surface | Current | Supporting |

<p>
  <img src="../.github/assets/readme/section-bars/engineering-references.svg" alt="ENGINEERING REFERENCES" width="100%">
</p>

| Path | Surface | Purpose | Status |
|---|---|---|---|
| `API.md` | Python API | API entry points and examples | Current |
| `CLI_CONTRACT.md` | CLI | Command contract and CLI semantics | Current |
| `CHEMOSENSE_EXTENSION.md` | Chemosense | Scope and extension notes | Current |
| `FIDELITY_SEMANTICS.md` | Metrics | Fidelity definitions and boundary language | Current |
| `TEST_MATRIX.md` | Validation | Test and gate coverage map | Current |
| `INTEGRATION_GUIDE.md` | Integration | Consumer guidance for repo surfaces | Current |
| `FAQ.md` | Reader support | Quick answers for install, release state, and scope limits | Current |
| `SUPPORT.md` | Reader support | Contact and issue-routing surface | Current |
| `LEGAL_BOUNDARIES.md` | Legal boundary | Compact legal and publication boundary | Current |
| `ARCH_TIGHTNESS_AUDIT.md` | Audit | Architecture-tightness review artifact | Current |
| `CI_POLICY.md` | CI | CI policy and workflow expectations | Current |
| `ZPE_IOT_SALES_BRIEF.md` | Operator/commercial | Internal briefing surface, not front-door authority | Current but non-canonical |

<p>
  <img src="../.github/assets/readme/section-bars/family-alignment.svg" alt="FAMILY ALIGNMENT" width="100%">
</p>

| Path | Purpose | Status | Authority level |
|---|---|---|---|
| `family/IOT_COMPATIBILITY_VECTOR.json` | Machine-readable IMC compatibility anchor | Current | Canonical for family pinning |
| `family/IOT_IMC_ALIGNMENT_REPORT.md` | IMC contract verification report | Current | Supporting |
| `family/IOT_RELEASE_NOTE_FOR_COORDINATION.md` | Cross-family release note | Current | Supporting |
| `../SUITE_COMPATIBILITY_VECTOR.json` | Suite linkage classification | Current | Supporting |
| `../LANE_INTERLOCKS.md` | Upstream/downstream boundaries | Current | Supporting |
| `../RELEASE_IMPACT.md` | What this repo changes and does not change | Current | Supporting |

<p>
  <img src="../.github/assets/readme/section-bars/evidence.svg" alt="EVIDENCE" width="100%">
</p>

| Path or pattern | Produces | Latest active example | Use for |
|---|---|---|---|
| `../validation/results/release_preflight_report_*.json` | Managed release gate snapshot | `../validation/results/release_preflight_report_20260321T205127.json` | Current gate truth |
| `../validation/results/dt_results_*.json` | Strict DT output | `../validation/results/dt_results_20260321T225304.json` | Validation closure |
| `../validation/results/bench_summary_E1_real_public_*.json` | E1 benchmark summary | `../validation/results/bench_summary_E1_real_public_20260321T225305.json` | Promoted benchmark authority |
| `../validation/results/fresh_env_smoke_*/smoke.log` | Cold-install smoke logs | `../validation/results/fresh_env_smoke_20260321T205515/smoke.log` | Install-path proof |
| `../validation/results/*manifest*.json` | Release and license manifests | `../validation/results/release_manifest_20260321T205457.json` | Packaging truth |
| `../release/RC_*/bundle_manifest.json` | Release bundle inventory | `../release/RC_20260321T225526/bundle_manifest.json` | Release packet proof |
| `../proofs/artifacts/*` | Human-readable proof artifacts | `../proofs/artifacts/REPO_TECHNICAL_ALIGNMENT_20260321.md` | Explanatory proof and receipts |

<p>
  <img src="../.github/assets/readme/section-bars/what-this-directory-is-not.svg" alt="WHAT THIS DIRECTORY IS NOT" width="100%">
</p>

| Path | Treatment | Why it is not front-door |
|---|---|---|
| `../project_docs/` | Historical/operator | Planning memory and runbooks, not current authority |
| `../validation/runbooks/` | Operational | Execution notes, not reader-facing truth |
| older `../release/RC_*` | Historical | Prior packets remain lineage only |
| `perf/` and historical prompt/PRD docs in `docs/` | Historical/operator | Useful context, not canonical status |
