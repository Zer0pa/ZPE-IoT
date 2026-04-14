# PRD: IoT External Baseline + DT-09 Semantics Correction

- Date: 2026-02-20
- Repo root: `/Users/zer0pa-build/ZPE IoT/zpe-iot`
- Priority: P0

## 1) Mission (Measurable)
Close remaining IoT engineering gap by:
1. Producing external baseline evidence tied to payload economics.
2. Correcting DT-09 gate semantics so native regressions cannot be masked.

## 2) Baseline Evidence Anchors
1. `/Users/zer0pa-build/ZPE IoT/zpe-iot/validation/destruct_tests/dt09_latency.py`
2. `/Users/zer0pa-build/ZPE IoT/zpe-iot/docs/BENCHMARKS.md`
3. `/Users/zer0pa-build/ZPE Multimodality/ZPE_IMC_TECHNICAL_DOSSIER.md`

## 3) In Scope / Out Of Scope
In scope:
1. IoT repo code/tests/benchmarks only.
2. DT-09 logic and strict replay validation.
3. External baseline benchmark outputs (including payload-size framing view).

Out of scope:
1. IMC/Bio code.
2. Narrative-only doc polish.

## 4) Comparator Contract
Comparator set must include at minimum:
1. ZPE
2. zlib
3. lz4
4. zstd

Plus payload-economics row:
1. transport payload bytes (including packet framing where applicable)
2. relative reduction vs raw baseline

## 5) Execution Order With Hard Gates
1. Gate A: baseline freeze and strict-replay capture.
2. Gate B: external comparator rerun with payload-economics outputs.
3. Gate C: DT-09 semantics fix (`no min(py,native)` masking).
4. Gate D: strict replay campaign rerun (`>=5`).
5. Gate E: packaging and claim delta.

## 6) Acceptance Criteria
1. DT-09 pass requires explicit non-masked semantics; if native present, native thresholds must independently pass.
2. Strict replay shows reproducible green runs after fix.
3. Comparator artifact includes payload-economics table.

## 7) Mandatory Artifacts
Output folder:
- `/Users/zer0pa-build/ZPE IoT/zpe-iot/validation/results/<DATE>_iot_external_baseline_dt09/`

Required:
1. `handoff_manifest.json`
2. `before_after_metrics.json`
3. `iot_external_baseline_results.json`
4. `dt09_semantics_recheck.json`
5. `falsification_results.md`
6. `claim_status_delta.md`
7. `command_log.txt`

## 8) Stop / Rollback
Stop if strict replay stability worsens or critical DT regressions appear.

## 9) No Hand-Wavy Claims
No latency-robustness closure claim without explicit python/native metric separation in artifacts.

## 10) Augmentation Addendum (2026-02-21, Evidence-Bound)
Purpose:
1. Extend this PRD from DT-09 semantics correction into full external-baseline closure and high-ROI codec augmentation.
2. Convert all material claims in `/Users/zer0pa-build/ZPE Multimodality/ZPE IoT_ Research Concept & Agent Execution Document.md` into executable gates with reproducible artifacts.

Evidence inputs (mandatory read before execution):
1. `/Users/zer0pa-build/ZPE Multimodality/ZPE IoT_ Research Concept & Agent Execution Document.md`
2. `/Users/zer0pa-build/ZPE Multimodality/ZPE_IMC_TECHNICAL_DOSSIER.md`
3. `/Users/zer0pa-build/ZPE IoT/zpe-iot/docs/BENCHMARKS.md`
4. `/Users/zer0pa-build/ZPE IoT/zpe-iot/validation/destruct_tests/dt09_latency.py`

## 11) Augmented Objectives (Measurable)
1. Preserve DT-09 strict semantics closure from Sections 1-9 (non-negotiable).
2. Close the documented 2/8 IoT baseline gap against zlib with an auditable augmentation path.
3. Produce public-grade external benchmark tables for:
   - Pcodec head-to-head,
   - TSBS IoT workload,
   - payload economics.
4. Remove machine-absolute path contamination from user-facing scripts/docs used in reproducibility flows.
5. Maintain or improve existing fidelity and determinism characteristics while augmenting compression path.

## 12) Claim Matrix (Augmented Wave)
| Claim ID | Claim | Pre-status | Evidence artifact(s) |
|---|---|---|---|
| IOT-A001 | DT-09 native-path masking removed and independently enforced | UNTESTED | `dt09_semantics_recheck.json`, `dt09_native_python_split.json` |
| IOT-A002 | External baseline table includes zpe/zlib/lz4/zstd/pcodec on common datasets | UNTESTED | `iot_external_baseline_results.json`, `external_baseline_table.csv` |
| IOT-A003 | Payload-economics table includes framing-overhead and effective transport bytes | UNTESTED | `payload_economics_table.csv` |
| IOT-A004 | RLE post-pass added and benchmarked with before/after impact | UNTESTED | `rle_postpass_ablation.json`, `before_after_metrics.json` |
| IOT-A005 | Prior 6/8 baseline is non-regressed and moved toward 8/8 under the same comparator contract | UNTESTED | `iot_external_baseline_results.json`, `baseline_delta_matrix.json` |
| IOT-A006 | Strict replay campaign remains stable after augmentation | UNTESTED | `strict_replay_campaign.json`, `determinism_replay_results.json` |
| IOT-A007 | Path portability risk reduced for execution-critical surfaces | UNTESTED | `path_portability_audit.json` |
| IOT-A008 | Benchmark pack is independently reproducible from runbook commands | UNTESTED | `reproducibility_proof.txt`, `command_log.txt` |

## 13) Dataset and Comparator Contract (Augmented)
Minimum comparator set (same data slices, same iteration policy):
1. zpe
2. zlib
3. lz4
4. zstd
5. pcodec (`pco_cli` or `pco` Python path)

Minimum dataset set to attempt (attempt-all; record infeasibility explicitly):
1. Existing 8 IoT datasets currently used by this repo baseline.
2. TSBS IoT generated workload.
3. At least one external public sensor dataset from the concept document (for example UCI Air Quality).

Attempt-all rule:
1. If any resource is not executable, record one of:
   - `IMP-LICENSE`
   - `IMP-ACCESS`
   - `IMP-COMPUTE`
   - `IMP-STORAGE`
   - `IMP-NOCODE`
2. Any `IMP-*` must include command, stderr, fallback, and affected claim IDs.

## 14) Execution Order (Augmented Hard Gates)
1. Gate A0: baseline freeze and strict replay snapshot.
2. Gate A1: comparator normalization (shared input fixtures, iterations, schema).
3. Gate A2: DT-09 semantics correction and explicit native/python split evidence.
4. Gate A3: pcodec head-to-head table generation.
5. Gate A4: TSBS workload generation and benchmark table.
6. Gate A5: RLE post-pass augmentation + ablation and regression sweep.
7. Gate A6: path-portability audit + targeted fixes for reproducibility-critical surfaces.
8. Gate A7: strict replay rerun and packaging of claim deltas.

Gate failure policy:
1. No downstream gate starts unless current gate is green or formally marked with `IMP-*` and impact statement.
2. Core claims (IOT-A001, IOT-A002, IOT-A006) cannot be marked PASS on proxy-only evidence.

## 15) Popperian Falsification Plan (Mandatory)
1. Falsify compression wins on low-variance and near-constant signals (the known weak shape class).
2. Falsify DT-09 under mixed native/python performance asymmetry to ensure no min-path masking remains.
3. Falsify RLE augmentation on adversarial alternating-token streams that should not compress.
4. Falsify reproducibility by re-running full benchmark pipeline in a fresh environment with only documented commands.
5. Falsify payload-economics claims by including framing overhead and verifying effective transport bytes.

## 16) Acceptance Criteria (Augmented Quantitative)
1. IOT-A001, IOT-A002, IOT-A003, IOT-A006, IOT-A008 must be PASS with direct artifacts.
2. No uncaught crashes in destruct and malformed campaigns introduced by augmentation.
3. Determinism replay remains hash-consistent across configured strict runs.
4. RLE augmentation must provide:
   - explicit win/loss matrix by dataset type,
   - no hidden threshold relaxation.
5. Any unresolved item must remain `UNTESTED` or `INCONCLUSIVE` with `IMP-*` evidence.

## 17) Mandatory Artifacts (Augmented Wave)
Output folder:
- `/Users/zer0pa-build/ZPE IoT/zpe-iot/validation/results/2026-02-21_iot_external_baseline_augmented/`

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

## 18) Stop Conditions and Rollback Criteria (Augmented)
Stop immediately if:
1. DT-09 semantics regress or become ambiguous.
2. strict replay stability regresses after augmentation.
3. new augmentation introduces uncaught crashes.

Rollback:
1. Revert to last green gate snapshot.
2. Patch minimally.
3. Re-run failed gate and all downstream gates.

## 19) No-Scope-Escape Rule
1. Work only inside `/Users/zer0pa-build/ZPE IoT/zpe-iot`.
2. No edits in IMC/Bio repos for this wave.
3. IMC integration claims must be referenced as external contract consumption only.
