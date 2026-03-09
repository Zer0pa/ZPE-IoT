# RUNBOOK_00_MASTER.md — ZPE-IoT Master Orchestration Runbook

**STOP. Read this entire document before doing anything.**
**You have no memory. This document IS your memory.**

---

## 0. What Is This Project?

You are building **ZPE-IoT**: an 8-primitive geometric compression SDK for IoT sensor time-series data. It encodes any 1D signal (temperature, vibration, accelerometer, pressure, GPS, voltage, current, flow) as directional chain codes, compresses with RLE, and produces a compact byte stream. The goal is ≥5x compression with <5% NRMSE on MCU-class hardware (≤4 KB RAM, no GPU, no cloud).

**This is a COMMERCIAL product.** The goal is a paying customer within 60 days.

**Full specification:** Read `ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md` in this same directory.

**Legacy reference:** Previous biosignal work lives in `Legacy Work/` — read-only. Do not modify.

---

## 1. Project Layout

```
/Users/prinivenpillay/ZPE IoT/                        ← PROJECT ROOT
├── ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md        ← THE PRD (source of truth)
├── PRD_06_ENTERPRISE_EXECUTION_v1.0.md               ← Enterprise execution PRD
├── RUNBOOK_00_MASTER.md                               ← THIS FILE (orchestration)
├── RUNBOOK_01_CORE_CODEC.md                           ← Phase 1 runbook
├── RUNBOOK_02_FALSIFICATION.md                        ← Phase 2 runbook
├── RUNBOOK_03_SDK_PACKAGE.md                          ← Phase 3 runbook
├── RUNBOOK_04_BENCHMARKS.md                           ← Phase 4 runbook
├── RUNBOOK_05_LAUNCH.md                               ← Phase 5 runbook
├── Legacy Work/                                       ← ZPE-Bio (read-only reference)
└── zpe-iot/                                           ← CODE REPOSITORY
```

## 2. Phase Gates — Current Status

**Update this table after completing each phase.** This is how the next agent finds where you left off.

| Phase | Runbook | Status | Date Completed | Gating DTs | Agent Notes |
|:---|:---|:---|:---|:---|:---|
| **Phase 0: Setup** | RUNBOOK_01 §0 | `PASSED` | 2026-02-13 | — | Repository scaffolded, manifests added, DT harness bootstrapped. |
| **Phase 1: Core Codec** | RUNBOOK_01 | `PASSED` | 2026-02-13 | DT-01..07, DT-11, DT-13 | Rust/Python codec + FFI + presets complete; gating DT set passes. |
| **Phase 2: Falsification** | RUNBOOK_02 | `PASSED` | 2026-02-13 | ALL P0+P1 | Final DT run: PASS=16, FAIL=0, SKIPPED=0 (`dt_results_20260213T221141.json`). |
| **Phase 3: SDK Package** | RUNBOOK_03 | `PASSED` | 2026-02-13 | pip install works | Wheel/install/examples/docs validated; TestPyPI/GitHub publish steps deferred (credentials). |
| **Phase 4: Benchmarks** | RUNBOOK_04 | `PASSED` | 2026-02-14 | PT-6 check | PT-6 FINAL on E1 is PASS (6/8 wins) with evidence-split artifacts and reproducibility metadata. |
| **Phase 5: Launch** | RUNBOOK_05 | `IN_PROGRESS` | — | First customer | Launch collateral complete; external publish/outreach/revenue milestones pending credentials and human execution. |
| **Phase H: Hardening Delta** | RUNBOOK_00 §10 + addenda | `IN_PROGRESS` | 2026-02-14 | Strict gates + provenance | Technical hardening gates are green; remaining step is user ratification for any publish action. |
| **Phase E: Enterprise Operationalisation** | PRD_06_ENTERPRISE_EXECUTION_v1.0 | `PASSED` | 2026-02-19 | E0..E9 gates | Enterprise hardening/packaging gates executed locally: strict DT PASS=21 with SKIPPED=0, E-tier benchmark split regenerated, RC bundle assembled, publish still deferred pending ratification. |

**Rules for updating status:**
- `NOT_STARTED` → `IN_PROGRESS` → `PASSED` or `FAILED_PIVOT`
- Only mark `PASSED` when ALL gating DTs for that phase pass
- If `FAILED_PIVOT`: write the pivot decision in "Agent Notes" and which PT-* trigger fired

---

## 3. Anti-Drift Protocol

**You WILL drift.** This protocol prevents it.

### 3.1 Session Start Checklist (MANDATORY)

Every time a new agent session begins, execute these steps IN ORDER:

```
STEP 1: Read this file (RUNBOOK_00_MASTER.md) — you are doing this now.
STEP 2: Check the Phase Gates table above.
          - Which phase are you in? ________
          - What is its status? ________
STEP 3: Run credential/tool preflight (GH/Kaggle/HF) per §3.5.
STEP 4: Open the corresponding RUNBOOK_0N file.
STEP 5: Search for the last step marked [x] (completed).
STEP 6: The next step marked [ ] is YOUR starting point.
STEP 7: Read the PRD sections referenced by that step.
STEP 8: Begin work.
```

### 3.2 Mid-Session Re-Grounding (Every 600 Seconds)

```
RE-GROUND 1: What phase am I in?
RE-GROUND 2: What step in the runbook am I on?
RE-GROUND 3: Does my current work align with the step description?
RE-GROUND 4: Have I skipped any steps? If yes, go back.
RE-GROUND 5: Have any DTs failed since last check? If yes, stop and diagnose.
RE-GROUND 6: Am I introducing code not referenced in the PRD? If yes, justify.
RE-GROUND 7: Am I doing something "academically interesting" instead of commercially necessary?
```

### 3.3 Session End Checklist (MANDATORY)

```
END 1: Update the Phase Gates table in THIS FILE with current status.
END 2: In the active RUNBOOK, mark completed steps as [x].
END 3: Write a 1-2 sentence summary in "Agent Notes" column.
END 4: If any DT failed, document: which DT, output, suspected cause.
END 5: Commit all code changes with message format: [STEP-N.M] description
END 6: Log session summary to CometML or docs/SESSION_LOG.md
```

### 3.4 Commercial Velocity Check (Every Phase End)

```
VELOCITY 1: Does what I built move us closer to a paying customer?
VELOCITY 2: Could I demo this to an IoT engineer right now?
VELOCITY 3: Is there anything blocking a sale that I should fix BEFORE the next phase?
VELOCITY 4: Am I gold-plating? Ship ugly > ship never.
```

### 3.5 Credential + Tooling Preflight (MANDATORY)

Run before any dataset pull, benchmark, or publish-adjacent step:

```bash
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot"
command -v gh >/dev/null || echo "MISSING: gh"
command -v kaggle >/dev/null || echo "MISSING: kaggle cli"
command -v huggingface-cli >/dev/null || echo "MISSING: huggingface-cli (optional if using HTTP token checks)"
gh auth status || echo "GH auth not active in this shell"
```

Rules:
1. If preflight fails, mark related tasks `BLOCKED` with exact reason.
2. Do not silently continue with fake/local substitute data for tasks requiring real-public sources.
3. Record which auth path is active:
   - GitHub App/device auth (`gh auth status`)
   - `GH_TOKEN`
   - `KAGGLE_API_TOKEN` or `KAGGLE_USERNAME` + `KAGGLE_KEY`
   - `HF_TOKEN`

---

## 4. Pivot Decision Framework

```
DT FAILED
  └─ Is the failure in the codec logic?
      ├─ YES → Check PT-1 (CR) or PT-2 (NRMSE) triggers
      │    ├─ Trigger fires → PIVOT: update PRD, re-implement
      │    └─ Trigger does not fire → FIX: patch and re-test
      └─ NO → Is the failure in infrastructure/tooling?
           ├─ YES → Fix infrastructure, re-test, do not modify codec
           └─ NO → Is the failure in the test itself?
                ├─ YES → Fix test, document, get user approval
                └─ NO → ESCALATE to user
```

**CRITICAL RULE:** Never modify a DT to make it pass. DTs are the immune system — weakening them kills the project.

### 4.1 Joint Trigger Rule (PT-1 + PT-2)

```
PT-1 = TRUE AND PT-2 = TRUE
  → ARCHITECTURE_BREAK
  → Freeze feature work
  → Options: (a) add entropy coding stage, (b) increase magnitude bits, (c) split modes
  → Re-run DT-01/DT-02 only after rescue completes
```

### 4.2 Gate Integrity Rule (No Silent Relaxation)

If a gate threshold is changed:
- Update PRD with rationale and data artifact
- Mark results as `PROVISIONAL`
- Do NOT mark phase `PASSED` on relaxed gates without user ratification

---

## 5. Innovation Protocol

### 5.1 At Success Points

```
INNOVATE 1: Log all metrics to CometML.
INNOVATE 2: Compare against stretch targets.
             - CR > 10x? → Document which signal type and why.
             - NRMSE < 1%? → Consider "lossless-equivalent" marketing claim.
INNOVATE 3: Check if new signal type should become a preset.
INNOVATE 4: Proceed to next phase.
```

### 5.2 At Failure Points

```
INNOVATE 1: Document failure fully (input, output, expected, actual).
INNOVATE 2: Root cause analysis:
             - Fundamental limitation? → Propose architecture change.
             - Tuning issue? → Run Pareto sweep.
             - Dataset pathology? → Add to DT-05.
INNOVATE 3: Update PRD with findings.
INNOVATE 4: Re-implement and re-test.
```

---

## 6. Exact Constants & Thresholds

See PRD §6 for the complete table. Key values:

| Constant | Value | Notes |
|:---|:---|:---|
| `TARGET_CR` | 5.0x | Minimum viable compression |
| `MAX_NRMSE` | 5% | Maximum distortion (BALANCED mode) |
| `MAX_RAM_BYTES` | 4096 | Embedded RAM budget |
| `DEFAULT_WINDOW_SIZE` | 256 | Samples per encode window |
| `LOG_MAG_TABLE_SIZE` | 64 | 6-bit magnitude index |

**These are NOT negotiable without PRD amendment + full DT re-run.**

---

## 7. File Naming Conventions

| Type | Convention | Example |
|:---|:---|:---|
| Rust source | `snake_case.rs` | `quantise.rs` |
| Python source | `snake_case.py` | `codec.py` |
| Test files | `test_<module>.py` | `test_codec.py` |
| DT scripts | `dt<NN>_<snake_name>.py` | `dt01_fidelity.py` |
| Documentation | `UPPER_SNAKE.md` | `RUNBOOK_01_CORE_CODEC.md` |
| Commits | `[STEP-N.M] description` | `[STEP-1.4] implement FAST mode` |
| CometML | `zpe-iot-phase-N-<desc>` | `zpe-iot-phase-2-full-dt-suite` |

---

## 8. Emergency Procedures

### 8.1 If You Don't Know Where You Are

```
1. Read this file
2. Check Phase Gates table
3. If table is empty/corrupt:
   a. Does zpe-iot/ exist? If no → Phase 0
   b. Does core/src/codec.rs exist? If no → Phase 0 or 1
   c. git log -n 5 to find last step
4. Resume
```

### 8.2 If Dependencies Won't Install

```
1. Check Cargo.toml / pyproject.toml versions in PRD §3.2
2. Use PINNED versions — do NOT upgrade
3. If pinned unavailable: find closest, document in DEPENDENCY_OVERRIDES.md, re-run all DTs
```

### 8.3 If CometML Is Unreachable

```
1. Set ZPE_IOT_COMET_OFFLINE=1
2. Log to docs/SESSION_LOG.md in markdown table format
3. DT runner MUST NOT fail due to CometML connectivity
4. Bulk-upload when CometML available again
```

### 8.4 If Benchmark Datasets Won't Download

```
1. Run: python validation/datasets/download_datasets.py
2. If download fails: check README.md for mirrors
3. Skip unavailable dataset — mark SKIPPED (not FAIL)
4. DT is only PASS when ALL datasets available and pass
```

---

## 9. Legacy Reference Guide

The previous ZPE-Bio biosignal codec work is in `Legacy Work/`. Key files:

| File | What To Learn From It |
|:---|:---|
| `zpe-bio/python/zpe_bio/codec.py` | Core encode/decode algorithm (generalise for IoT) |
| `zpe-bio/core/rust/src/rle.rs` | RLE compression (reuse as-is) |
| `zpe-bio/core/rust/src/codec.rs` | Rust no_std implementation pattern |
| `zpe-bio/core/rust/src/ffi.rs` | C FFI binding pattern |
| `zpe-bio/python/zpe_bio/test_codec.py` | Property-based test patterns |
| `zpe-bio/validation/destruct_tests/` | DT framework and runner |
| `RUNBOOK_02_FALSIFICATION.md` | DT implementation examples |

**DO NOT modify Legacy Work files.** They are read-only reference.

---

## 10. Addendum 2026-02-14 — Hardening Sprint (ACTIVE)

This addendum is append-only and does not replace prior history.

### 10.1 Active Overrides

`[SUPERSEDED-2026-02-14]` The permissive SKIP interpretation for mandatory gates is no longer valid for phase progression.

From this point:

1. Mandatory gate `SKIPPED` == `FAIL_GATING`.
2. Phase 4 and Phase 5 claims are `PROVISIONAL` if based on proxy datasets.
3. External publishing (PyPI/crates.io/GitHub public launch) stays deferred until hardening gate completion and user ratification.

### 10.2 Hardening Task Board

- [x] **H-01:** Implement strict gate semantics in DT runner (`mandatory SKIP` must return non-zero)
- [x] **H-02:** Remove PASS-on-proxy behavior from mandatory DTs (especially DT-06 and DT-16)
- [x] **H-03:** Introduce dataset provenance verifier and manifest schema enforcement
- [x] **H-04:** Promote DS-01..DS-08 from proxy to `real_public` evidence class
- [x] **H-05:** Re-run full DT suite in strict mode (PASS=all mandatory, SKIP=0)
- [x] **H-06:** Re-run benchmark suite on `real_public` data and regenerate PT-6 verdict
- [x] **H-07:** Add claim-tier labels to benchmark/sales docs (`E0/E1/E2`)
- [x] **H-08:** Execute architecture tightness audit (remove superfluous/circuitous paths)
- [x] **H-09:** Execute one intersectional breakthrough branch and ablation-test it

### 10.3 Hardening Completion Gate

Mark hardening complete only when all are true:

1. H-01..H-09 are checked.
2. Latest strict DT artifact reports `PASS=mandatory`, `SKIPPED=0`.
3. PT-6 is confirmed on `real_public` datasets.
4. `RUNBOOK_05` launch deferral gate is cleared.
5. User explicitly approves release actions.

### 10.4 Session Start Addendum (Mandatory)

Before resuming any phase:

1. Read this addendum section.
2. Confirm whether hardening tasks are pending.
3. If pending, prioritize hardening work over publish/community launch tasks.

### 10.5 Hardening Evidence Snapshot (2026-02-14)

- Strict DT run artifact: `zpe-iot/validation/results/dt_results_20260214T105519.json`
  - Summary: `PASS=21, FAIL=0, SKIPPED=0, BLOCKED=0, NOT_IMPLEMENTED=0, TIMEOUT=0`
- Provenance verifier: `zpe-iot/validation/datasets/verify_provenance.py`
  - DS-01..DS-08 manifest entries set to `real_public` with validated raw/transform hashes.
- Benchmark artifacts:
  - Overall: `zpe-iot/validation/results/bench_summary_20260214T103739.json`
  - E1 split: `zpe-iot/validation/results/bench_summary_E1_real_public_20260214T103739.json`
  - PT-6 FINAL (E1): `PASS` (6/8 wins)
  - PT-6 PROVISIONAL (E0): `NOT_AVAILABLE`
- WI-1 ablation artifact: `zpe-iot/validation/results/wi1_ablation_20260214T103817.json`
  - Result: retained behind feature flag `ZPE_IOT_WI1_ENTROPY_STAGE`.
- Launch policy remains deferred pending explicit user publish ratification.

---

## 11. Addendum 2026-02-14B — Draconian-Proof Local Closure (ACTIVE)

This addendum is append-only and keeps all prior sections as historical memory.

### 11.1 Supersession Notes

- `[SUPERSEDED-2026-02-14B by §11.2]` Hardening complete is necessary but not sufficient for draconian-proof status.
- `[SUPERSEDED-2026-02-14B by §11.2]` Any WI-1 retention decision without packed-byte decode-path benchmarking is provisional.
- `[SUPERSEDED-2026-02-14B by §11.2]` Any benchmark/report label that can emit `FINAL` for zero-dataset tiers is invalid.

### 11.2 Local Closure Task Board (No External Inputs)

- [ ] **DCL-01:** WI-1 wire-path ablation integrity
  - Benchmark control/candidate using packed bytes (`encode` bytes -> `decode` bytes), not stream shortcuts.
  - Run repeated trials (`n >= 5`) and include p50/p99 latency.
  - Compute `gate_regression_detected` from strict DT reruns, not hardcoded constants.
- [ ] **DCL-02:** Evidence-tier label correctness
  - Patch report generation so any tier with `total=0` cannot be labeled `FINAL`.
  - Allowed labels: `NOT_AVAILABLE`, `PROVISIONAL`, `FINAL` (only when `total>0` and rule satisfied).
- [ ] **DCL-03:** Threshold governance convergence
  - Reconcile DT numeric thresholds and PRD constants table.
  - If thresholds changed, append explicit ratification note in PRD constants/governance sections.
- [ ] **DCL-04:** Baseline immutability for DT-16
  - Pin baseline artifacts under versioned directory and hash manifest.
  - DT-16 must consume pinned baseline identity, not "latest file wins" behavior.
- [ ] **DCL-05:** Public-claim consistency
  - Align `README.md`, `docs/BENCHMARKS.md`, `docs/ZPE_IOT_SALES_BRIEF.md`, and outreach template to active evidence tier metrics.
- [ ] **DCL-06:** Demo fairness and comparability
  - `scripts/customer_demo.py` must use comparable encode/decode measurement envelopes and state method limits explicitly.
- [ ] **DCL-07:** Intersectional performance branch (local)
  - Implement at least one physics-informed improvement behind feature flag and run ablation:
    1. multi-scale residual quantisation (coarse+fine),
    2. derivative-domain entropy shaping,
    3. periodic predictor for quasi-harmonic signals.
  - Retain only if strict gates stay green and E1 metrics improve materially.

### 11.3 Draconian-Proof Completion Gate

Mark this addendum complete only when all are true:

1. DCL-01..DCL-07 are checked with linked artifacts.
2. Strict DT rerun remains green (`SKIPPED=0`, `BLOCKED=0`) for mandatory set.
3. Benchmark/report outputs obey evidence-label rule for zero-dataset tiers.
4. PRD constants/governance and DT code thresholds are numerically aligned.
5. Claim text in README/sales/outreach reflects current E1/E2 truth.
6. User ratifies readiness status before any external publish action.

### 11.4 Resume Order (Mandatory)

On every new execution session:

1. Read RUNBOOK_00 §10 and §11.
2. If §11 is not complete, execute §11 tasks before any launch/publication tasks.
3. Treat unresolved §11 items as P0 blockers for publish readiness.

---

**This document is the spine of the project. If it is corrupted or lost, the project is lost. Treat it with care.**

### 11.5 Closure Update (2026-02-14C)

- [x] **DCL-01:** WI-1 wire-path ablation integrity complete
  - Artifact: `zpe-iot/validation/results/wi1_ablation_20260214T201525.json`
  - Protocol: `encode bytes -> decode bytes`, repeats `= 5`, per-dataset and aggregate p50/p99 latency included.
  - `gate_regression_detected` computed from strict DT differential (no hardcoded constant).
- [x] **DCL-02:** Evidence-tier label correctness enforced
  - Artifact: `zpe-iot/validation/results/bench_summary_E2_real_customer_20260214T200706.json`
  - Rule outcome: `total=0` now emits `pt6_label=NOT_AVAILABLE`, `pt6_status=NOT_AVAILABLE`.
  - Coverage: `zpe-iot/python/tests/test_benchmark_labels.py` and `zpe-iot/validation/destruct_tests/dt19_claim_tier_compliance.py`.
- [x] **DCL-03:** Threshold governance convergence closed
  - Source-of-truth file: `zpe-iot/validation/destruct_tests/thresholds.py`
  - Audit table: `zpe-iot/docs/THRESHOLD_GOVERNANCE_AUDIT.md`
  - PRD ratification: `ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md` §16.2.
- [x] **DCL-04:** DT-16 baseline immutability active
  - Baseline tag: `draconian_20260214C`
  - Artifacts:
    - `zpe-iot/validation/results/baseline/draconian_20260214C/bench_summary.json`
    - `zpe-iot/validation/results/baseline/draconian_20260214C/manifest.json`
    - `zpe-iot/validation/results/baseline/ACTIVE_BASELINE_TAG`
  - Enforcement: `zpe-iot/validation/destruct_tests/dt16_benchmark_regression.py` (explicit tag + hash verification).
- [x] **DCL-05:** Public-claim consistency synchronized
  - Updated: `zpe-iot/README.md`, `zpe-iot/docs/BENCHMARKS.md`, `zpe-iot/docs/ZPE_IOT_SALES_BRIEF.md`, `zpe-iot/docs/OUTREACH_TEMPLATE.md`.
- [x] **DCL-06:** Demo fairness and comparability tightened
  - Script: `zpe-iot/scripts/customer_demo.py`
  - Artifact: `zpe-iot/validation/results/customer_demo_20260214T202358.json`
  - Includes comparable encode/decode envelope, repeats/warmup, and method metadata.
- [x] **DCL-07:** Intersectional branch executed locally (ZH-1)
  - Feature flag: `ZPE_IOT_ZH1_DERIVATIVE_STAGE`
  - Artifact: `zpe-iot/validation/results/zh1_ablation_20260214T202338.json`
  - Decision: **rejected / default-off** due introduced mandatory regressions (`DT-10`, `DT-11`) despite CR gain.

### 11.6 Strict Gate Snapshot (2026-02-14C)

- Strict DT artifact: `zpe-iot/validation/results/dt_results_20260214T202758.json`
- Summary: `PASS=21, FAIL=0, SKIPPED=0, BLOCKED=0, NOT_IMPLEMENTED=0, TIMEOUT=0`
- Mandatory strict set: green (no mandatory SKIP/BLOCKED/FAIL).


### 11.7 Supersession Update (2026-02-14C2)

- `[SUPERSEDED-2026-02-14C2 by §11.7]` WI artifact `wi1_ablation_20260214T201525.json` replaced by rerun `wi1_ablation_20260214T204017.json` after mandatory-only strict differential semantics fix.
- `[SUPERSEDED-2026-02-14C2 by §11.7]` ZH artifact `zh1_ablation_20260214T202338.json` replaced by rerun `zh1_ablation_20260214T204801.json`.
- `[SUPERSEDED-2026-02-14C2 by §11.7]` Strict DT snapshot `dt_results_20260214T202758.json` replaced by final strict artifact `dt_results_20260214T205143.json`.

---

## 12. Addendum 2026-02-19 — Enterprise Operationalisation Program (ACTIVE)

This addendum is append-only and does not replace prior history.

### 12.1 Program Declaration

1. Enterprise completion is governed by `PRD_06_ENTERPRISE_EXECUTION_v1.0.md`.
2. Program phases are `E0..E9`.
3. Reporting mode for executing agent: final report only unless hard-blocked.

### 12.2 Supersession Notes

- `[SUPERSEDED-2026-02-19 by §12.3]` \"hardening-complete\" is not equivalent to \"enterprise-maximal\".
- `[SUPERSEDED-2026-02-19 by §12.3]` Packaging readiness claims are provisional until E1/E4/E8 gates pass.

### 12.3 Enterprise Program Entry Gate

Mark entry as active when all are true:

1. Latest strict DT mandatory set is green.
2. Latest benchmark E-tier split artifacts exist.
3. Agent confirms canonical code repository path in final report.

### 12.4 Resume Order (Enterprise)

When `Phase E` status is `IN_PROGRESS`:

1. Read `RUNBOOK_00` §10, §11, and §12.
2. Read `PRD_06_ENTERPRISE_EXECUTION_v1.0.md`.
3. Execute phases `E0..E9` sequentially.
4. Defer external publish actions until explicit user ratification.

### 12.5 Execution Update (2026-02-19)

- [x] **E0 Repository Formalization**
  - `REPO_TOPOLOGY.md` created at project root.
  - Root hygiene file `.gitignore` added.
  - `zpe-iot/scripts/sync_memory_docs.sh` + `zpe-iot/project_docs/` snapshot active.
- [x] **E1 Packaging Hardening**
  - `python/pyproject.toml` license/readme metadata corrected.
  - `python/README.md` added for package sdist context.
  - Fresh-venv smoke run succeeded for CLI commands.
- [x] **E2 Coherence/Cohesion**
  - Shared fidelity semantics module: `zpe-iot/validation/metrics/fidelity.py`.
  - Policy doc: `zpe-iot/docs/FIDELITY_SEMANTICS.md`.
  - Benchmark tables now label `NRMSE(window-normalized)` explicitly.
- [x] **E3 Test Matrix + Coverage**
  - Coverage threshold enforced in `python/pyproject.toml` (`>=85%`).
  - Coverage artifact: `zpe-iot/validation/results/coverage/python_coverage.xml`.
  - Matrix doc: `zpe-iot/docs/TEST_MATRIX.md`.
- [x] **E4 CI/Governance**
  - Workflows: `zpe-iot/.github/workflows/ci.yml`, `zpe-iot/.github/workflows/packaging_warnings.yml`.
  - Policy: `zpe-iot/docs/CI_POLICY.md`.
- [x] **E5 Security/Provenance**
  - Docs: `zpe-iot/SECURITY.md`, `zpe-iot/SUPPORT.md`.
  - Scan artifact: `zpe-iot/validation/results/vulnerability_scan_20260219T003747.json`.
  - SBOM/license/release manifests regenerated (`zpe-iot/validation/results/*_20260219T011216.json`).
- [x] **E6 Executable Reliability**
  - CLI hardened with `--json`, chunked CSV path, diagnostics, deterministic runtime errors.
  - Contract doc: `zpe-iot/docs/CLI_CONTRACT.md`.
- [x] **E7 Performance Program**
  - Profiling artifacts: `zpe-iot/validation/results/perf_profile_hot_paths_20260219T023929.json`, `zpe-iot/docs/perf/profile_hot_paths_20260219T023929.txt`.
  - WI/ZH ablations rerun; both rejected due strict-gate regression despite CR gain.
- [x] **E8 RC Packaging**
  - Metadata/docs completed (`CONTRIBUTING.md`, `.github/CODEOWNERS`, `docs/RELEASE_CHECKLIST.md`).
  - RC bundle built: `zpe-iot/release/RC_20260219T031240/`.
- [x] **E9 Closeout Verification**
  - Final strict DT artifact: `zpe-iot/validation/results/dt_results_20260219T030940.json` (`PASS=21`, `SKIPPED=0`).
  - Final benchmark split artifacts: `zpe-iot/validation/results/bench_summary_*_20260219T030604.json`.
  - External publishing remains deferred pending explicit user ratification.

---

## 13. Addendum 2026-02-20 — Chemosense Extension Integration (ACTIVE)

This addendum is append-only and does not replace prior history.

### 13.1 Program Declaration

1. Scope: integrate smell+taste augmentation into in-repo Python SDK without external path dependency.
2. Constraint: copy-only ingestion from external capability source; no symlink dependency.
3. Gate policy: preserve strict draconian gating (`pytest coverage >=85`, Rust tests, strict DT suite).
4. Forward execution authority for chemosense hardening/packaging: `PRD_07_CHEMOSENSE_ENTERPRISE_v1.0.md`.

### 13.2 Supersession Notes

- `[SUPERSEDED-2026-02-20 by §13.3]` External import references to `artifacts.packetgram.*` are invalid for canonical in-repo execution.
- `[SUPERSEDED-2026-02-20 by §13.3]` Chemosense code presence alone is insufficient without package wiring + deterministic validation.

### 13.3 Execution Update (2026-02-20)

- [x] **C0 Recon + Copy-In**
  - Source dossier reviewed: `/Users/prinivenpillay/ZPE Multimodality/ZPE_IMC_TECHNICAL_DOSSIER.md`.
  - Modules copied into:
    - `zpe-iot/python/zpe_iot/chemosense/common/`
    - `zpe-iot/python/zpe_iot/chemosense/smell/`
    - `zpe-iot/python/zpe_iot/chemosense/taste/`
- [x] **C1 In-Tree Dependency Rewire**
  - All `artifacts.packetgram.*` imports replaced with local `zpe_iot.chemosense.common.*` paths.
  - Package entrypoints added:
    - `zpe-iot/python/zpe_iot/chemosense/__init__.py`
    - `zpe-iot/python/zpe_iot/chemosense/common/__init__.py`
    - `zpe-iot/python/zpe_iot/chemosense/smell/__init__.py`
    - `zpe-iot/python/zpe_iot/chemosense/taste/__init__.py`
- [x] **C2 SDK/CLI Integration**
  - Root namespace export wired via `zpe-iot/python/zpe_iot/__init__.py`.
  - CLI command added: `zpe-iot chemosense-smoke --json`.
  - Diagnostics now exposes chemosense capability state.
- [x] **C3 Test + Coverage Hardening**
  - New tests:
    - `zpe-iot/python/tests/test_chemosense.py`
    - `zpe-iot/python/tests/test_chemosense_extended.py`
    - `zpe-iot/python/tests/test_cli.py` (chemosense smoke coverage)
  - Full Python gate: `41 passed`, coverage `87.76%` (threshold `>=85%`).
- [x] **C4 Regression Gates**
  - Rust: `cargo test` PASS; `cargo clippy -- -D warnings` PASS.
  - Strict DT suite PASS:
    - `zpe-iot/validation/results/dt_results_20260220T030203.json`
    - `PASS=21, FAIL=0, SKIPPED=0, BLOCKED=0, NOT_IMPLEMENTED=0, TIMEOUT=0`.
- [x] **C5 Documentation**
  - Added: `zpe-iot/docs/CHEMOSENSE_EXTENSION.md`.
  - Updated quickstarts: `zpe-iot/README.md`, `zpe-iot/python/README.md`.

### 13.4 Remaining External Blockers

1. Public release/publish remains deferred pending explicit user ratification.
2. E2 real-customer evidence tier remains external-data dependent.

### 13.5 PRD-07 Phase P0->P5 Completion Update (2026-02-20)

- [x] **P0 Reproducibility Freeze (re-run complete)**
  - Python gate: `zpe-iot/python` -> `pytest -q` PASS (`47 passed`, coverage `87.57%`, threshold `>=85%`).
  - Rust gate: `zpe-iot/core` -> `cargo test` PASS, `cargo clippy -- -D warnings` PASS.
  - Strict DT gate: `zpe-iot/validation/results/dt_results_20260220T035518.json` -> `PASS=25, FAIL=0, SKIPPED=0, BLOCKED=0`.
  - Latency gate regression repaired via native FFI zero-copy input path (`python/zpe_iot/_native.py`).

- [x] **P1 API Cohesion + Error Surface**
  - Contract layer added: `zpe-iot/python/zpe_iot/chemosense/contract.py`.
  - Typed errors added/exported: `ChemosenseError`, `ChemosenseSchemaError`, `ChemosensePacketError`.
  - CLI/API semantic unification: `zpe-iot/python/zpe_iot/cli.py::chemosense_smoke` now uses `run_smoke_flow()`.
  - Contract tests added: `zpe-iot/python/tests/test_chemosense_contract.py`.
  - CLI module-path test added: `zpe-iot/python/tests/test_cli.py::test_module_execution_chemosense_smoke_json`.
  - Contract docs expanded: `zpe-iot/docs/CHEMOSENSE_EXTENSION.md`.

- [x] **P2 Performance Tightness + Profiling**
  - Fusion scheduler hot path tightened to single-pass packet extraction:
    `zpe-iot/python/zpe_iot/chemosense/taste/fusion_scheduler.py`.
  - Chemosense profiler added:
    `zpe-iot/validation/benchmarks/profile_chemosense.py`.
  - Perf artifacts generated:
    - `zpe-iot/validation/results/perf_profile_chemosense_20260220T035037.json`
    - `zpe-iot/docs/perf/chemosense_profile_20260220T035037.md`
  - Measurable median latency improvement recorded (fusion ingest p50 improvement ~`19.18%`).

- [x] **P3 Data Realism + Provenance**
  - Chemosense dataset adapters built under:
    `zpe-iot/validation/datasets/raw/chemosense/`.
  - Manifest added:
    `zpe-iot/validation/datasets/manifest_chemosense.json` (E-tier, source/license/hash metadata).
  - Build + verify scripts added:
    - `zpe-iot/validation/datasets/build_chemosense_adapters.py`
    - `zpe-iot/validation/datasets/verify_chemosense_provenance.py`
  - Provenance verification PASS at `E1` for `CS-01..CS-03`.

- [x] **P4 DT + Benchmark Extension**
  - Added DTs and wired into strict runner:
    - `zpe-iot/validation/destruct_tests/dt22_modality_bit_collision.py`
    - `zpe-iot/validation/destruct_tests/dt23_zlayer_decode_integrity.py`
    - `zpe-iot/validation/destruct_tests/dt24_fusion_order_determinism.py`
    - `zpe-iot/validation/destruct_tests/dt25_malformed_packet_resilience.py`
  - Runner map updated:
    `zpe-iot/validation/destruct_tests/run_all_dts.py`.
  - Chemosense benchmark summary generated:
    `zpe-iot/validation/results/bench_summary_chemosense_20260220T035032.json`.

- [x] **P5 Packaging + RC Generation (Publish Deferred)**
  - CLI contract validated:
    - `zpe-iot chemosense-smoke --json` PASS
    - `python -m zpe_iot.cli chemosense-smoke --json` PASS
  - Chemosense RC bundler added:
    `zpe-iot/scripts/build_chemosense_rc_bundle.py`.
  - RC output generated:
    `zpe-iot/release/RC_CHEMOSENSE_20260220T035529/`.
  - Checklist aligned:
    `zpe-iot/docs/RELEASE_CHECKLIST.md`.

### 13.6 Final State (PRD-07)

1. Gate posture: strict and draconian (mandatory `SKIPPED` continues to fail strict mode).
2. External publishing: still deferred; no PyPI/crates.io/public push executed.
3. Commercial readiness status: **READY_FOR_USER_RATIFICATION** (local execution scope complete).
4. Remaining external blockers:
   - Real-customer E2 evidence remains external-input dependent.
   - Public publication remains blocked pending explicit user ratification.

### 13.7 Artifact Supersession Notes (2026-02-20)

- `[SUPERSEDED-2026-02-20 by rerun]` Earlier chemosense RC bundle path `zpe-iot/release/RC_CHEMOSENSE_20260220T035529/`.
  - Active chemosense RC bundle path: `zpe-iot/release/RC_CHEMOSENSE_20260220T035756/`.
- `[SUPERSEDED-2026-02-20 by full strict + delta checks]` Intermediate strict artifacts.
  - Full strict reference artifact remains: `zpe-iot/validation/results/dt_results_20260220T035518.json` (`PASS=25, FAIL=0, SKIPPED=0`).
  - Post-doc delta check artifact: `zpe-iot/validation/results/dt_results_20260220T035752.json` (`DT-19/21/25 PASS`).

---

## 14. Addendum 2026-02-20B — Touch + Mental Expansion Planning (ACTIVE)

This addendum is append-only and does not overwrite prior sections.

### 14.1 Recon Summary

External capability trees verified:

1. Touch source available at:
   - `/Users/prinivenpillay/ZPE Multimodality/touch/source/`
2. Mental source available at:
   - `/Users/prinivenpillay/ZPE Multimodality/mental/source/`

Both include dedicated tests and runbooks in their originating workstreams.

### 14.2 Why Touch/Mental Were Not Included in First Chemosense Pass

1. First pass scope was constrained to smell+taste closure requested in active stream.
2. Touch and mental stacks use separate import topology (`from source.*`) and required a full additional rewire cycle.
3. Touch had only placeholder packet framing in local fusion path and needed canonical module copy to avoid drift.
4. Mental uses distinct direction profile logic (8-dir + 12-dir D6 exact mode), requiring separate contract/tests before safe merge.

### 14.3 Gap Register to Close

1. Copy and normalize touch modules into `zpe-iot/python/zpe_iot/chemosense/touch/`.
2. Copy and normalize mental modules into `zpe-iot/python/zpe_iot/chemosense/mental/`.
3. Rewrite `from source.*` imports to in-repo package paths.
4. Replace touch placeholder helpers with canonical touch pack/scheduler integration.
5. Add touch+mental tests inside `zpe-iot/python/tests/` with branch and malformed-path coverage.
6. Extend strict DT set with touch/mental-specific invariants and contamination/fusion checks.

### 14.4 Execution Authority

Forward execution authority for this expansion:

- `PRD_08_TOUCH_MENTAL_ENTERPRISE_v1.0.md`

### 14.5 Publish Constraint

No external publish is authorized by this addendum. Public release remains user-ratified only.

### 14.6 PRD-08 Delta Closure Update (2026-02-20C)

- [x] **T1 Touch Ingestion + Rewire**
  - Canonical touch modules copied into `zpe-iot/python/zpe_iot/chemosense/touch/`.
  - `from source.*` imports removed from local chemosense tree.
  - Touch tests added: `zpe-iot/python/tests/test_chemosense_touch.py`.

- [x] **T2 Mental Ingestion + Rewire**
  - Canonical mental modules copied into `zpe-iot/python/zpe_iot/chemosense/mental/`.
  - D6_12 + COMPASS_8 direction profiles preserved with deterministic replay tests.
  - Mental tests added: `zpe-iot/python/tests/test_chemosense_mental.py`.

- [x] **T3 Cohesion, Fusion, CLI**
  - Contract expanded with touch/mental APIs in `zpe-iot/python/zpe_iot/chemosense/contract.py`.
  - CLI smoke now reports smell+taste+touch+mental in `zpe-iot/python/zpe_iot/cli.py`.
  - Placeholder touch generator removed from smoke flow (`touch_placeholder_removed: true`).

- [x] **T4 DT Extension + Mandatory Closure Checks**
  - Added DTs:
    - `zpe-iot/validation/destruct_tests/dt26_import_hygiene.py`
    - `zpe-iot/validation/destruct_tests/dt27_cross_modality_contamination.py`
  - Strict runner updated for DT-26/27 in `zpe-iot/validation/destruct_tests/run_all_dts.py`.
  - Strict artifact: `zpe-iot/validation/results/dt_results_20260220T043708.json` (`PASS=27, FAIL=0, SKIPPED=0`).

- [x] **T5 Benchmark/Claim Sync (Local, Publish Deferred)**
  - Core benchmark refresh:
    - `zpe-iot/validation/results/bench_summary_20260220T043931.json`
    - `zpe-iot/validation/results/bench_summary_E1_real_public_20260220T043931.json`
    - `zpe-iot/validation/results/bench_summary_E2_real_customer_20260220T043931.json`
  - Chemosense touch/mental benchmark artifact:
    - `zpe-iot/validation/results/bench_summary_chemosense_20260220T043714.json`
  - Claims/docs synchronized in:
    - `zpe-iot/README.md`
    - `zpe-iot/docs/BENCHMARKS.md`
    - `zpe-iot/docs/ZPE_IOT_SALES_BRIEF.md`
    - `zpe-iot/docs/OUTREACH_TEMPLATE.md`

#### Mandatory Closure Checks (Executed)

1. Import hygiene command (required):
   - `rg "from source\\.|import source\\.|artifacts\\.packetgram" zpe-iot/python/zpe_iot/chemosense/`
   - Result: zero matches (enforced by `DT-26 PASS`).
2. Cross-modality contamination check (required):
   - Mixed mental/smell/taste/touch decode matrix.
   - Result: zero false positives (enforced by `DT-27 PASS`).

#### Supersession Notes

- `[SUPERSEDED-2026-02-20C]` Prior chemosense benchmark reference artifact `bench_summary_chemosense_20260220T035032.json`.
  - Active reference: `bench_summary_chemosense_20260220T043714.json`.
- `[SUPERSEDED-2026-02-20C]` Prior strict DT reference artifact `dt_results_20260220T035752.json`.
  - Active reference: `dt_results_20260220T043708.json`.


### 14.7 Supersession Update (2026-02-20D)

- `[SUPERSEDED-2026-02-20D]` Strict artifact `zpe-iot/validation/results/dt_results_20260220T043708.json`.
  - Active strict reference artifact: `zpe-iot/validation/results/dt_results_20260220T045408.json` (`PASS=27, FAIL=0, SKIPPED=0`).


### 14.8 Final Verification + WI-1 Delta Note (2026-02-20E)

- [x] **Final strict baseline revalidation**
  - Artifact: `zpe-iot/validation/results/dt_results_20260220T050007.json` (`PASS=27, FAIL=0, SKIPPED=0`).

- [x] **WI-1 ablation rerun (repeats >=5) executed**
  - Artifact: `zpe-iot/validation/results/wi1_ablation_20260220T050410.json`.
  - Outcome: `retained=false` due strict gate differential regression (`introduced_failures`: DT-10, DT-11) despite CR gain.
  - Default flag remains disabled (`ZPE_IOT_WI1_ENTROPY_STAGE` not retained for production default).

- `[SUPERSEDED-2026-02-20E]` Strict reference artifact `zpe-iot/validation/results/dt_results_20260220T045408.json`.
  - Active strict reference artifact: `zpe-iot/validation/results/dt_results_20260220T050007.json`.

