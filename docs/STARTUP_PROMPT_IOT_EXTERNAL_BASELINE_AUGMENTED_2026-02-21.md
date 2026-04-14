# Startup Prompt: IoT External Baseline + Codec Augmentation Agent

Date: 2026-02-21
Scope root: `/Users/zer0pa-build/ZPE IoT/zpe-iot`
PRD to execute first: `/Users/zer0pa-build/ZPE IoT/zpe-iot/docs/PRD_IOT_EXTERNAL_BASELINE_AND_DT09_2026-02-20.md`

## Mission
Execute the augmented IoT baseline-and-augmentation wave end-to-end with evidence-first discipline:
1. keep DT-09 semantics strict and non-masked,
2. produce reproducible external baseline tables,
3. execute high-ROI codec augmentation (RLE post-pass) with before/after evidence,
4. package a final claim delta with no hand-wavy closure.

## Hard Rules
1. Read the PRD fully before any code edits.
2. Runbook-first is mandatory: extend runbooks before coding.
3. Stay lane-local: edit only inside `/Users/zer0pa-build/ZPE IoT/zpe-iot`.
4. Do not relax thresholds to force PASS.
5. No claim upgrades without direct artifact evidence.
6. If blocked, classify using `IMP-LICENSE`, `IMP-ACCESS`, `IMP-COMPUTE`, `IMP-STORAGE`, or `IMP-NOCODE` with command/error proof.
7. Report only once at the end.

## Required Sequence
1. Extend runbook memory:
   - `validation/runbooks/RUNBOOK_IOT_WAVE1_MASTER.md`
   - add an augmented-wave section with gates A0..A7 from PRD Sections 14-17.
2. Freeze baseline and strict replay (Gate A0).
3. Normalize comparator harness and schema (Gate A1).
4. Execute DT-09 semantics correction and native/python split evidence (Gate A2).
5. Run pcodec head-to-head benchmarks and publish table (Gate A3).
6. Run TSBS IoT benchmark path and publish payload-economics outputs (Gate A4).
7. Implement and validate RLE post-pass with ablation and regression sweep (Gate A5).
8. Run path portability audit and fix reproducibility-critical path leaks (Gate A6).
9. Re-run strict replay + determinism campaign + package claim delta (Gate A7).

## Mandatory Artifacts
Output folder must be:
`/Users/zer0pa-build/ZPE IoT/zpe-iot/validation/results/2026-02-21_iot_external_baseline_augmented/`

Required files:
1. `handoff_manifest.json`
2. `before_after_metrics.json`
3. `iot_external_baseline_results.json`
4. `external_baseline_table.csv`
5. `payload_economics_table.csv`
6. `dt09_semantics_recheck.json`
7. `dt09_native_python_split.json`
8. `rle_postpass_ablation.json`
9. `baseline_delta_matrix.json`
10. `strict_replay_campaign.json`
11. `determinism_replay_results.json`
12. `path_portability_audit.json`
13. `falsification_results.md`
14. `claim_status_delta.md`
15. `reproducibility_proof.txt`
16. `command_log.txt`
17. `impracticality_decisions.json`

## Completion Contract
Return only after full execution. Final response must include:
1. gate-by-gate status,
2. before/after metrics,
3. claim-status delta with exact evidence paths,
4. unresolved items with `IMP-*` reason codes,
5. explicit GO/NO-GO recommendation for this IoT wave.
