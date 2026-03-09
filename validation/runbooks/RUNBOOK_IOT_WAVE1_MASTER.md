# RUNBOOK IoT Wave-1 Master

Created: 2026-02-20T17:38:50Z
PRD: /Users/prinivenpillay/ZPE IoT/zpe-iot/docs/PRD_IOT_WAVE1_RELEASE_REFINEMENT.md
Scope root: /Users/prinivenpillay/ZPE IoT/zpe-iot
IMC freeze: contract_version=wave1.0, vector_sha256=9c8b905f6c1d30d057955aa9adf0f7ff9139853494dca673e5fbe69f24fba10e

## Execution Protocol
1. Runbook-first execution.
2. Execute phases 0..6 in strict order.
3. For each phase: execute -> capture logs -> gate -> patch -> rerun -> advance on green.

## Phase Ledger
- [ ] Phase 0 Baseline Freeze
- [ ] Phase 1 Checklist-to-Code Conversion
- [ ] Phase 2 Build and Install Integrity
- [ ] Phase 3 Wire Compatibility Hardening
- [ ] Phase 4 Security and Provenance Automation
- [ ] Phase 5 IMC Alignment Publication
- [ ] Phase 6 RC Rehearsal and Handover

## Append-Only Execution Log

### 2026-02-20T17:38:50Z Phase 0 start
- Verified IMC vector hash + contract version against frozen values.
- Proceeding to baseline inventory and baseline chain.

### 2026-02-20T17:45:22Z Phase 0 completed
- [x] Phase 0 Baseline Freeze
- Inventory artifact: validation/results/iot_wave1_phase0_inventory.txt
- Baseline artifact: validation/results/iot_wave1_phase0_baseline.txt

### 2026-02-20T18:18:45Z Phase 1 completed
- [x] Phase 1 Checklist-to-Code Conversion
- Artifacts:
  - validation/results/iot_wave1_phase1_preflight_dryrun.txt
  - validation/results/iot_wave1_phase1_preflight_schema.json
  - validation/results/iot_wave1_phase1_preflight_report.json
- Gate: PASS (critical_failures=0)

### 2026-02-20T18:18:45Z Phase 2 completed
- [x] Phase 2 Build and Install Integrity
- Artifacts:
  - validation/results/iot_wave1_phase2_build_clean.txt
  - validation/results/iot_wave1_phase2_fresh_env_smoke.txt
  - validation/results/iot_wave1_phase2_checksums.txt
- Gate: PASS

### 2026-02-20T18:18:45Z Phase 3 completed
- [x] Phase 3 Wire Compatibility Hardening
- Artifacts:
  - validation/results/iot_wave1_phase3_golden_packets.txt
  - validation/results/iot_wave1_phase3_malformed_behavior.txt
- Gate: PASS

### 2026-02-20T18:18:45Z Phase 4 completed
- [x] Phase 4 Security and Provenance Automation
- Artifacts:
  - validation/results/iot_wave1_phase4_security_scan.txt
  - validation/results/iot_wave1_phase4_sbom_manifest.txt
  - validation/results/iot_wave1_phase4_release_attestation.txt
- Gate: PASS

### 2026-02-20T18:18:45Z Phase 5 completed
- [x] Phase 5 IMC Alignment Publication
- Artifacts:
  - docs/family/IOT_IMC_ALIGNMENT_REPORT.md
  - docs/family/IOT_COMPATIBILITY_VECTOR.json
  - docs/family/IOT_RELEASE_NOTE_FOR_COORDINATION.md
  - validation/results/iot_wave1_phase5_alignment.txt
- Gate: PASS

### 2026-02-20T18:18:45Z Phase 6 completed
- [x] Phase 6 RC Rehearsal and Handover
- Artifacts:
  - validation/results/iot_wave1_phase6_rc_rehearsal.txt
  - validation/results/iot_wave1_phase6_preflight_report.json
  - validation/results/iot_wave1_phase6_preflight_schema.json
- Gate: PASS (total=18, pass=17, fail=0, critical_failures=0)

### 2026-02-20T18:18:45Z Phase Ledger status update (append-only)
- [x] Phase 0 Baseline Freeze
- [x] Phase 1 Checklist-to-Code Conversion
- [x] Phase 2 Build and Install Integrity
- [x] Phase 3 Wire Compatibility Hardening
- [x] Phase 4 Security and Provenance Automation
- [x] Phase 5 IMC Alignment Publication
- [x] Phase 6 RC Rehearsal and Handover

### 2026-02-20T18:16:29Z phase closure
- [x] Phase 1 Checklist-to-Code Conversion
- [x] Phase 2 Build and Install Integrity
- [x] Phase 3 Wire Compatibility Hardening
- [x] Phase 4 Security and Provenance Automation
- [x] Phase 5 IMC Alignment Publication
- [x] Phase 6 RC Rehearsal and Handover

### 2026-02-20T20:29:01Z External Baseline + DT-09 PRD kickoff
- PRD: /Users/prinivenpillay/ZPE IoT/zpe-iot/docs/PRD_IOT_EXTERNAL_BASELINE_AND_DT09_2026-02-20.md
- Scope lock: operate only inside /Users/prinivenpillay/ZPE IoT/zpe-iot.

Atomic execution steps (hard-gated):
1. Gate A baseline freeze:
   - Capture baseline DT-09 semantics state and strict DT snapshot.
   - Save baseline metrics and command transcript to external-baseline result folder.
2. Gate B comparator rerun:
   - Re-run external comparators (ZPE/zlib/lz4/zstd) with payload-economics fields.
   - Emit comparator artifact with transport payload bytes and relative reduction vs raw.
3. Gate C DT-09 semantics correction:
   - Enforce explicit python/native separation; no `min(py,native)` masking.
   - Add/refresh tests to prevent regression of masking behavior.
4. Gate D strict replay >=5:
   - Run strict DT suite at least 5 consecutive times in pinned `.venv`.
   - Record pass/fail variance and DT-level outcomes.
5. Gate E packaging + claims:
   - Produce claim delta and falsification artifacts.
   - Emit handoff manifest and before/after metrics only from passing evidence.

Rollback notes:
- If strict replay worsens or critical DT regressions appear, stop execution and retain prior stable gate evidence as current claim basis.
- Do not change thresholds unless separately ratified with explicit evidence note.
- Do not mark claims upgraded unless corresponding mandatory artifact exists and gate is green.

### 2026-02-20T21:21:03Z External Baseline + DT-09 execution completed
- PRD: /Users/prinivenpillay/ZPE IoT/zpe-iot/docs/PRD_IOT_EXTERNAL_BASELINE_AND_DT09_2026-02-20.md
- Output root: /Users/prinivenpillay/ZPE IoT/zpe-iot/validation/results/2026-02-20_iot_external_baseline_dt09

Gate outcomes:
- Gate A baseline freeze and strict capture: PASS
- Gate B external comparator payload economics: PASS
- Gate C DT-09 non-masked semantics fix: PASS
- Gate D strict replay campaign (>=5): PASS (5/5)
- Gate E packaging and claim delta: PASS

Mandatory artifacts:
- validation/results/2026-02-20_iot_external_baseline_dt09/handoff_manifest.json
- validation/results/2026-02-20_iot_external_baseline_dt09/before_after_metrics.json
- validation/results/2026-02-20_iot_external_baseline_dt09/iot_external_baseline_results.json
- validation/results/2026-02-20_iot_external_baseline_dt09/dt09_semantics_recheck.json
- validation/results/2026-02-20_iot_external_baseline_dt09/falsification_results.md
- validation/results/2026-02-20_iot_external_baseline_dt09/claim_status_delta.md
- validation/results/2026-02-20_iot_external_baseline_dt09/command_log.txt

Rollback note:
- Stop conditions were not triggered; strict replay stability improved to deterministic 5/5 green with mandatory failures empty.

### 2026-02-21T02:19:06Z Augmented external-baseline execution kickoff (A0..A7)
- PRD: /Users/prinivenpillay/ZPE IoT/zpe-iot/docs/PRD_IOT_EXTERNAL_BASELINE_AND_DT09_2026-02-20.md
- Scope lock: /Users/prinivenpillay/ZPE IoT/zpe-iot only (no IMC/Bio edits).
- Mandatory evidence inputs read:
  - /Users/prinivenpillay/ZPE Multimodality/ZPE IoT_ Research Concept & Agent Execution Document.md
  - /Users/prinivenpillay/ZPE Multimodality/ZPE_IMC_TECHNICAL_DOSSIER.md
  - /Users/prinivenpillay/ZPE IoT/zpe-iot/docs/BENCHMARKS.md
  - /Users/prinivenpillay/ZPE IoT/zpe-iot/validation/destruct_tests/dt09_latency.py

Augmented gates (hard order):
1. A0 baseline freeze + strict replay snapshot
2. A1 comparator normalization (fixtures/iterations/schema)
3. A2 DT-09 semantics split evidence
4. A3 pcodec head-to-head
5. A4 TSBS workload generation + benchmark
6. A5 RLE post-pass ablation + regression sweep
7. A6 path-portability audit + reproducibility-surface fixes
8. A7 strict replay rerun + claim packaging

Rollback and stop discipline:
- Stop on strict replay stability regression or critical DT regressions.
- No threshold relaxation; no claim upgrade without direct artifact evidence.
- Any infeasible resource classified as IMP-LICENSE/IMP-ACCESS/IMP-COMPUTE/IMP-STORAGE/IMP-NOCODE with command+stderr proof.
