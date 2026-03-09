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
| **Phase E: Enterprise Operationalisation** | PRD_06_ENTERPRISE_EXECUTION_v1.0 | `NOT_STARTED` | — | E0..E9 gates | Recon indicates strong pilot readiness but not enterprise-maximal; execute E-phases before final packaging ratification. |

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
