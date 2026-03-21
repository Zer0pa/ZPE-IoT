# PRD_06_ENTERPRISE_EXECUTION_v1.0.md

Status: ACTIVE  
Owner: Zer0pa Lab  
Date: 2026-02-19  
Scope: `/Users/prinivenpillay/ZPE IoT/zpe-iot` and project memory docs in `/Users/prinivenpillay/ZPE IoT`

---

## 0) Executive Intent

This PRD defines an end-to-end enterprise-hardening and packaging program for ZPE-IoT.

The directive interpreted into engineering requirements:

1. Perform a real recon of current state (not assumptions).
2. Decide whether system is already at a practical maximum and packageable.
3. If not at maximum, define concrete improvements to get there.
4. Move forward on repository formalization inside this folder.
5. Resolve executable reliability and enterprise code quality (coherence/cohesion).
6. Produce a coding-agent-executable, granular plan with strict gates.
7. Require long-horizon reporting at the end only.

---

## 1) Recon Snapshot (2026-02-19)

### 1.1 What Is Already Strong

1. Rust core quality gates pass:
   - `cargo test` passes.
   - `cargo clippy -- -D warnings` passes.
2. Python tests pass in project venv:
   - `../.venv/bin/python -m pytest -q` -> `11 passed`.
3. Strict destructive gate passes:
   - `PASS=21, FAIL=0, SKIPPED=0, BLOCKED=0`.
   - Latest verified artifact: `validation/results/dt_results_20260219T020752.json`.
4. E-tier benchmark labeling logic exists (E0/E1/E2) with guardrail tests.
5. Baseline pinning for DT-16 exists (`validation/results/baseline/...`).

### 1.2 What Is Not Enterprise-Complete Yet

1. Repo topology is ambiguous:
   - Root folder has a git repo with no commits.
   - Product code lives in nested git repo `zpe-iot` with actual history.
2. Python packaging warns during build:
   - Deprecation warning for `project.license` table format.
   - sdist warning: missing README in `python/` package root.
3. CI/CD is absent:
   - No `.github/workflows/` in active code repo.
4. Release controls are partial:
   - No formal release checklist automation.
   - No enterprise-grade provenance bundle standard for release candidates.
5. Metric semantics need one explicit policy closure:
   - Fidelity metric framing in DT and benchmark views can still be interpreted differently by non-technical audiences.

### 1.3 Decision

ZPE-IoT is technically strong and pilot-ready, but not yet enterprise-maximal.

Decision:

1. Do not treat this as final maximum yet.
2. Execute enterprise-hardening and repository formalization phases first.
3. Package immediately after gates in this PRD are green.

---

## 2) Program Outcomes

By completion, we will have:

1. A single canonical product repository path and governance policy.
2. Deterministic build/test/lint/benchmark CI with release gates.
3. Executable surfaces (CLI + Python API + C/Rust boundary) hardened and tested.
4. Metric semantics explicitly unified and documented.
5. Enterprise documentation set (security, supportability, release runbook, provenance bundle).
6. Release artifacts reproducible from one command chain.
7. Public-package-ready candidate (publish command remains user-ratified).

---

## 3) Non-Negotiable Constraints

1. Append-only memory style for PRD/runbooks.
2. No weakening of destructive tests to force pass.
3. No silent fallback from missing prerequisites to PASS-like outcomes.
4. No external publish without explicit user ratification phrase `publish now`.
5. Final report only at program end (no interim narrative unless hard-blocked).

---

## 4) Execution Contract (Agent)

The executing coding agent must:

1. Run phases E0 through E9 in order.
2. Mark each checklist item with evidence artifact references.
3. Commit at phase boundaries with deterministic commit messages.
4. Report once at the end with:
   - full gate status,
   - artifact index,
   - unresolved external blockers only.

### 4.1 Reporting Mode

Long-horizon final-only reporting:

1. No intermediate progress messages.
2. Only final completion report unless blocked by missing credentials/network/toolchain impossibility.

---

## 5) Canonical Phase Plan

## Phase E0: Repository Formalization

Objective:

1. Remove ambiguity between root repo and nested product repo.

Tasks:

- [ ] E0.1 Confirm canonical code repo remains `/Users/prinivenpillay/ZPE IoT/zpe-iot`.
- [ ] E0.2 In root folder, create `REPO_TOPOLOGY.md` documenting:
  - root memory docs role,
  - canonical code repo path,
  - sync/export policy.
- [ ] E0.3 Add script `scripts/sync_memory_docs.sh` in code repo to snapshot relevant PRD/runbooks into `zpe-iot/project_docs/` for release bundles.
- [ ] E0.4 Add `.gitignore` and hygiene in root repo to exclude large transient artifacts.
- [ ] E0.5 Create `zpe-iot/project_docs/` and import current canonical docs snapshot.

Gate E0 PASS when:

1. Topology is explicit and reproducible.
2. Any new engineer can answer "which repo is canonical" in < 30 seconds.

Artifacts:

1. `REPO_TOPOLOGY.md` (root)
2. `zpe-iot/project_docs/` snapshot
3. `zpe-iot/scripts/sync_memory_docs.sh`

---

## Phase E1: Packaging and Executable Hardening

Objective:

1. Make Python/Rust packaging warning-free and install-smoke-tested.

Tasks:

- [ ] E1.1 Update `python/pyproject.toml` license field to SPDX string form.
- [ ] E1.2 Add/readme wiring so sdist has a valid README in `python/` context.
- [ ] E1.3 Add `python/README.md` package-facing short doc or map root README explicitly.
- [ ] E1.4 Ensure `zpe-iot` CLI command works from wheel install in clean venv.
- [ ] E1.5 Add CLI smoke tests for `compress`, `decompress`, `info`, `benchmark` command paths.
- [ ] E1.6 Validate error codes/messages for malformed inputs and missing numeric columns.

Validation commands:

```bash
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot/python"
../.venv/bin/python -m build
python -m venv /tmp/zpe-enterprise-smoke
source /tmp/zpe-enterprise-smoke/bin/activate
pip install dist/zpe_iot-*.whl
zpe-iot --help
deactivate
```

Gate E1 PASS when:

1. Build emits no deprecation/missing-README warnings.
2. CLI smoke path works in fresh environment.

Artifacts:

1. `python/dist/*.whl`, `python/dist/*.tar.gz`
2. CLI smoke transcript in `docs/SESSION_LOG.md`

---

## Phase E2: Coherence and Cohesion Refactor

Objective:

1. Tighten architecture semantics and eliminate metric interpretation ambiguity.

Tasks:

- [ ] E2.1 Define a single fidelity semantics policy doc:
  - dataset-global NRMSE vs window-local NRMSE,
  - where each is allowed and why.
- [ ] E2.2 Refactor DT and benchmark code to use named metric modes from one shared module.
- [ ] E2.3 Add explicit labels in benchmark tables (for example: `NRMSE(window-normalized)` vs `NRMSE(dataset-normalized)`).
- [ ] E2.4 Ensure DT-01 and benchmark fidelity views cannot be confused in commercial docs.
- [ ] E2.5 Run architecture tightness audit update with before/after map.

Gate E2 PASS when:

1. Metric semantics are unambiguous in code and docs.
2. DT and benchmark modules import shared fidelity policy constants.

Artifacts:

1. `docs/FIDELITY_SEMANTICS.md`
2. Updated `docs/ARCH_TIGHTNESS_AUDIT.md`
3. Added/updated tests validating mode labels.

---

## Phase E3: Enterprise Test Matrix + Coverage

Objective:

1. Establish a release-grade automated quality matrix.

Tasks:

- [ ] E3.1 Add Python coverage tooling (pytest-cov) and enforce minimum threshold.
- [ ] E3.2 Add Rust coverage or at least expanded invariance/property suites for codec core.
- [ ] E3.3 Add integration tests for:
  - packet round-trip across presets,
  - CLI end-to-end from csv to packet to csv,
  - baseline pinning and hash mismatch failure.
- [ ] E3.4 Add golden-file tests for benchmark label rule (`NOT_AVAILABLE`, `PROVISIONAL`, `FINAL`).

Gate E3 PASS when:

1. Python coverage threshold >= 85% on package modules.
2. Core invariance tests cover deterministic encode/decode edge cases.

Artifacts:

1. Coverage reports in `validation/results/coverage/`
2. Test matrix summary doc `docs/TEST_MATRIX.md`

---

## Phase E4: CI/CD and Branch Governance

Objective:

1. Make quality gates mandatory in automation, not manual habit.

Tasks:

- [ ] E4.1 Add GitHub Actions workflows (or equivalent CI) for:
  - Rust test + clippy,
  - Python tests + build,
  - strict DT smoke subset,
  - benchmark report generation sanity.
- [ ] E4.2 Add branch protection policy doc (`main` requires green checks).
- [ ] E4.3 Add conventional release tags and changelog generation flow.
- [ ] E4.4 Add fail-fast workflow for packaging warnings treated as errors.

Gate E4 PASS when:

1. CI runs reproducibly from clean checkout.
2. No direct-to-main quality bypass path remains.

Artifacts:

1. `.github/workflows/*.yml`
2. `docs/CI_POLICY.md`

---

## Phase E5: Security, Compliance, and Provenance Bundle

Objective:

1. Introduce enterprise trust artifacts expected by procurement/security teams.

Tasks:

- [ ] E5.1 Add `SECURITY.md`, `SUPPORT.md`, and vulnerability disclosure process.
- [ ] E5.2 Add dependency vulnerability scan scripts for Python and Rust.
- [ ] E5.3 Generate SBOM for release candidate (CycloneDX or SPDX).
- [ ] E5.4 Add license manifest for third-party dependencies.
- [ ] E5.5 Extend release manifest to include:
  - commit SHA,
  - build toolchain hashes,
  - benchmark artifact hashes,
  - DT artifact hashes.

Gate E5 PASS when:

1. Security/provenance docs are complete and reproducible.
2. No high-severity dependency vulnerabilities unresolved (or documented exceptions).

Artifacts:

1. `SECURITY.md`, `SUPPORT.md`
2. `validation/results/release_manifest_*.json`
3. `validation/results/sbom_*.json`

---

## Phase E6: Executable Reliability and UX

Objective:

1. Make the product executable surface predictable under real operator behavior.

Tasks:

- [ ] E6.1 Improve CLI help and examples for non-expert operators.
- [ ] E6.2 Add explicit machine-readable output mode (`--json`) for automation.
- [ ] E6.3 Add streaming/chunked file handling path for large CSV inputs.
- [ ] E6.4 Add deterministic exit-code contract doc.
- [ ] E6.5 Add native-acceleration detection diagnostics (`zpe_iot._native.available()`).

Gate E6 PASS when:

1. CLI is scriptable and deterministic across success/failure paths.
2. Large-file path and error path are tested.

Artifacts:

1. Updated `python/zpe_iot/cli.py`
2. `docs/CLI_CONTRACT.md`
3. CLI integration tests.

---

## Phase E7: Enterprise Performance Program

Objective:

1. Improve real-world performance without violating determinism and gate stability.

Tasks:

- [ ] E7.1 Profile encode/decode hot paths on representative E1 datasets.
- [ ] E7.2 Implement one approved low-risk optimization at a time (feature-flagged).
- [ ] E7.3 Run strict DT + benchmark reruns per optimization.
- [ ] E7.4 Keep only optimizations with measurable gain and no gate regressions.

Gate E7 PASS when:

1. Measurable improvement or explicit no-regression conclusion is documented.
2. All mandatory gates remain green.

Artifacts:

1. `docs/perf/` profiling reports
2. Optimization ablation artifacts

---

## Phase E8: Repository Creation and Release Packaging

Objective:

1. Formalize publish-ready repository and release candidate bundle in this folder.

Tasks:

- [ ] E8.1 Prepare repository metadata:
  - `README.md` (enterprise claim-safe),
  - `LICENSE`,
  - `SECURITY.md`,
  - `CONTRIBUTING.md`,
  - `CODEOWNERS`.
- [ ] E8.2 Add release checklist and one-command preflight script.
- [ ] E8.3 Produce release candidate bundle:
  - wheel/sdist,
  - benchmark summaries,
  - strict DT artifact,
  - provenance manifest,
  - SBOM.
- [ ] E8.4 Verify local installation and sample CLI workflow from release bundle.
- [ ] E8.5 Prepare but do not execute external publish commands until user ratifies.

Gate E8 PASS when:

1. Repo is packageable and enterprise-readable.
2. Release bundle is complete and reproducible from clean checkout.

Artifacts:

1. `release/RC_<timestamp>/...`
2. `docs/RELEASE_CHECKLIST.md`

---

## Phase E9: Program Closeout

Objective:

1. Produce final single-report handoff for leadership decision.

Tasks:

- [ ] E9.1 Final strict DT run.
- [ ] E9.2 Final benchmark split run (E0/E1/E2).
- [ ] E9.3 Final coherence audit summary.
- [ ] E9.4 Final repo/package readiness statement.
- [ ] E9.5 List external-only blockers (if any).

Gate E9 PASS when:

1. Final report is complete and evidence-linked.

---

## 6) Mandatory Commands by Phase

```bash
# Baseline quality (must stay green)
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot/core"
cargo test
cargo clippy -- -D warnings

cd "/Users/prinivenpillay/ZPE IoT/zpe-iot/python"
../.venv/bin/python -m pytest -q
../.venv/bin/python -m build

cd "/Users/prinivenpillay/ZPE IoT/zpe-iot"
.venv/bin/python validation/destruct_tests/run_all_dts.py --strict-gates
.venv/bin/python validation/benchmarks/run_benchmarks.py
.venv/bin/python validation/benchmarks/generate_report.py
```

---

## 7) Final Report Template (Single End Report)

The executing agent must return exactly one final comprehensive report containing:

1. **Program Status**
   - E0..E9 status table (`PASSED` / `FAILED_PIVOT` / `BLOCKED_EXTERNAL`).
2. **Quality Summary**
   - cargo test/clippy results,
   - pytest + coverage,
   - strict DT counts and artifact path.
3. **Performance Summary**
   - PT-6 by evidence tier,
   - mean CR and fidelity interpretation labels.
4. **Packaging Summary**
   - wheel/sdist build status,
   - install smoke results,
   - CLI smoke results.
5. **Security/Provenance Summary**
   - SBOM presence,
   - vulnerability scan summary,
   - release manifest hash list.
6. **Repository Readiness**
   - canonical repo declaration,
   - release candidate bundle path.
7. **External-Only Blockers**
   - credentials/publish/ratification items only.
8. **Decision Recommendation**
   - `READY_FOR_USER_RATIFICATION` or `NOT_READY` with causes.

---

## 8) Commercial Readiness Criteria

Commercially ready for controlled pilot scale when all are true:

1. Strict DT mandatory set: green.
2. E1 claims are truthful, reproducible, and label-safe.
3. Packaging/install/CLI path verified from fresh environment.
4. Security and provenance artifacts are present.
5. Repository governance and CI are active.
6. No unresolved P0/P1 engineering risks.

---

## 9) External Blockers (Expected)

These remain outside local code execution scope:

1. Final remote repo create/push if credentials unavailable.
2. Public package publication credentials and release ratification.
3. Real-customer E2 data consent and benchmark capture.

These must be explicitly listed, not hidden.

---

## 10) Supersession and Memory Preservation

This PRD is additive and does not delete historical plans.

Reference lineage:

1. `ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md` remains canonical historical source.
2. `RUNBOOK_00_MASTER.md` remains orchestration spine.
3. This document is execution PRD for enterprise-hardening completion and packaging transition.

---

## 11) Execution Completion Update (2026-02-19)

- [x] **E0** Repository topology formalized (`REPO_TOPOLOGY.md`, root `.gitignore`, memory sync script/snapshot).
- [x] **E1** Python packaging hardened (`python/pyproject.toml` SPDX/readme), clean build + fresh-venv CLI smoke.
- [x] **E2** Fidelity semantics unified (`validation/metrics/fidelity.py`, `docs/FIDELITY_SEMANTICS.md`, labeled benchmark tables).
- [x] **E3** Coverage/test matrix enforced (`>=85%` coverage, `docs/TEST_MATRIX.md`, invariance/integration tests).
- [x] **E4** CI and branch governance added (`.github/workflows/*.yml`, `docs/CI_POLICY.md`).
- [x] **E5** Security/provenance bundle artifacts generated (`vulnerability_scan`, `sbom`, `license_manifest`, `release_manifest`).
- [x] **E6** CLI reliability hardening complete (`--json`, chunked CSV path, diagnostics, `docs/CLI_CONTRACT.md`).
- [x] **E7** Performance program completed with profiling + feature-flag ablations (WI-1/ZH-1 rejected due strict regressions).
- [x] **E8** Release packaging completed locally (`docs/RELEASE_CHECKLIST.md`, `scripts/release_preflight.sh`, RC bundle).
- [x] **E9** Final closeout evidence captured (`dt_results_20260219T030940.json`, benchmark split `20260219T030604`).

Decision state after execution:

1. Local engineering gates are green and enterprise artifacts are assembled.
2. External publish actions remain deferred pending explicit user ratification.
