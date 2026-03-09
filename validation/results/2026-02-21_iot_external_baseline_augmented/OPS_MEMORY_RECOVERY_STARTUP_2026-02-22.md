# OPS Memory Recovery Startup (2026-02-22)

## 1) Lane mission and current technical status
- Mission: preserve adjudication-grade evidence while removing lane-local superfluous artifacts and enabling path-portable restart.
- Current lane status: gates `{'A0': 'PASS', 'A1': 'PASS', 'A2': 'PASS', 'A3': 'PASS', 'A4': 'PASS', 'A5': 'PASS', 'A6': 'PASS', 'A7': 'PASS'}`; claims `{'IOT-A001': 'PASS', 'IOT-A002': 'PASS', 'IOT-A003': 'PASS', 'IOT-A004': 'PASS', 'IOT-A005': 'FAIL', 'IOT-A006': 'PASS', 'IOT-A007': 'PASS', 'IOT-A008': 'PASS'}`; overall `GO_QUALIFIED`.
- PT-6 snapshot: `{'status': 'PASS', 'label': 'FINAL', 'wins': 6, 'total': 8}`.

## 2) Exact latest adjudicated bundle root
- Absolute: `/Users/prinivenpillay/ZPE IoT/zpe-iot/validation/results/2026-02-21_iot_external_baseline_augmented`
- Workspace-relative: `validation/results/2026-02-21_iot_external_baseline_augmented`
- Variable-based: `${LANE_ROOT}`

## 3) Read-first list (ordered)
1. `validation/results/2026-02-21_iot_external_baseline_augmented/quality_gate_scorecard.json` | `${LANE_ROOT}/quality_gate_scorecard.json`
2. `validation/results/2026-02-21_iot_external_baseline_augmented/handoff_manifest.json` | `${LANE_ROOT}/handoff_manifest.json`
3. `validation/results/2026-02-21_iot_external_baseline_augmented/claim_status_delta.md` | `${LANE_ROOT}/claim_status_delta.md`
4. `validation/results/2026-02-21_iot_external_baseline_augmented/runpod_readiness_manifest.json` | `${LANE_ROOT}/runpod_readiness_manifest.json`
5. `validation/results/2026-02-21_iot_external_baseline_augmented/residual_risk_register.md` | `${LANE_ROOT}/residual_risk_register.md`
6. `validation/results/2026-02-21_iot_external_baseline_augmented/commercialization_risk_register.md` | `${LANE_ROOT}/commercialization_risk_register.md`
7. `validation/results/2026-02-21_iot_external_baseline_augmented/internet_evidence_log.md` | `${LANE_ROOT}/internet_evidence_log.md`
8. `validation/results/2026-02-21_iot_external_baseline_augmented/OPS_CLEANUP_REPORT_2026-02-22.md` | `${LANE_ROOT}/OPS_CLEANUP_REPORT_2026-02-22.md`
9. `validation/results/2026-02-21_iot_external_baseline_augmented/OPS_CLEANUP_MANIFEST_2026-02-22.json` | `${LANE_ROOT}/OPS_CLEANUP_MANIFEST_2026-02-22.json`

## 4) Resume checklist (step-by-step)
1. Resolve dynamic roots and verify lane context before running any command.
2. Confirm required adjudication files exist and parse cleanly.
3. Run strict DT gate and benchmark reproduction commands with pinned venv.
4. Regenerate claim/gate deltas only after evidence files are present.
5. If any new artifact is uncertain, place it in quarantine and document rationale before deletion.

## 5) Reproduction commands (local and RunPod if applicable)
```bash
# Dynamic roots (portable)
WORKSPACE_ROOT="$(cd "$(dirname "${LANE_ROOT:-$PWD}")/../../.." && pwd)"
LANE_ROOT="${WORKSPACE_ROOT}/validation/results/2026-02-21_iot_external_baseline_augmented"
cd "${WORKSPACE_ROOT}"

# Local strict verification chain
.venv/bin/python validation/destruct_tests/run_all_dts.py --strict-gates
.venv/bin/python validation/benchmarks/run_benchmarks.py
.venv/bin/python validation/benchmarks/generate_report.py
.venv/bin/python -m pytest -q
cargo test --release

# Optional RunPod replay (only if IMP-COMPUTE emerges)
# Mirror the local strict chain in a pinned container image and write outputs back under ${LANE_ROOT}.
```

## 6) Critical artifact map (what each key file proves)
| Artifact | Proof role |
|---|---|
| `quality_gate_scorecard.json` | Central adjudication score and GO/NO-GO summary. |
| `handoff_manifest.json` | Gate/claim status matrix + required adjudication file contract. |
| `claim_status_delta.md` | Claim transitions with direct evidence links. |
| `runpod_readiness_manifest.json` | Whether external compute is required for closure. |
| `internet_evidence_log.md` | External source/license attempts and blocker-exhaustion evidence. |
| `residual_risk_register.md` | Remaining technical risks for next wave. |
| `commercialization_risk_register.md` | Claim-language/commercialization risk constraints. |

## 7) Known blockers and exact evidence paths
- `IOT-A005` remains `FAIL`: `${LANE_ROOT}/a005_resolution_path1_legacy_contract.json`, `${LANE_ROOT}/a005_resolution_path2_preset_autotune.json`, `${LANE_ROOT}/a005_resolution_path3_external_datasets.json`.
- `IMP-ACCESS` (UCI id=501 API availability): `${LANE_ROOT}/a005_resolution_path3_external_datasets.json`.
- `IMP-STORAGE` (optional fpzip baseline path): `${LANE_ROOT}/a005_resolution_path4_fpzip_tool_attempt.json`.

## 8) Decision rules (GO/NO_GO/INCONCLUSIVE)
- `GO`: strict gates pass, required adjudication files present, and claim statuses are evidence-backed with no missing required files.
- `NO_GO`: any mandatory gate fails, required adjudication files missing, or evidence links are broken.
- `INCONCLUSIVE`: only allowed when evidence acquisition is genuinely blocked and classified with IMP-* proof; otherwise force PASS/FAIL adjudication.

## 9) Path portability note
- Root may change by username/machine; resolve paths dynamically from current workspace.
- Always record both workspace-relative paths and variable-based paths (`${HOME}`, `${WORKSPACE_ROOT}`, `${LANE_ROOT}`).

## 10) First 30/60/120-minute restart plan
- 0-30 min: verify roots, read scorecard/handoff/claim delta, run integrity checks on required files.
- 30-60 min: rerun strict DT + benchmark chain, confirm deterministic outputs and claim consistency.
- 60-120 min: resolve any IMP-* blockers with logged attempts, update adjudication artifacts, and prepare ratification-ready summary.
