# RUNBOOK IoT Rx Strict Stability

Append-only execution log for strict-gate reproducibility hardening.

## 2026-02-20T14:43:29Z - Hardening Delta Closure

### Objective
- Make strict DT gate reproducible in pinned `.venv`.
- Ensure RC bundles can only include full strict DT evidence (27 DT results, strict true, mandatory failures empty).

### Implemented Changes
- `validation/destruct_tests/dt09_latency.py`
  - Added deterministic timed-sampling harness with GC control.
  - Added explicit warmup/sample loop metadata in result payload.
  - Increased warmup iterations to mitigate cold-start latency transients.
  - Kept strict thresholds unchanged.
- `scripts/build_chemosense_rc_bundle.py`
  - Added full strict DT validation (`strict_gates=true`, `results_count=27`, `mandatory_failures=[]`).
  - Bundle build now fails when no qualifying strict DT artifact exists.
  - Manifest now records `strict_dt_evidence` contract fields.
- `python/tests/test_chemosense_rc_bundle_strict.py`
  - Added regression tests for strict DT artifact selection and failure behavior.

### Verification Evidence
- Python tests:
  - `validation/results/pytest_latest_20260220T124239.log`
- Strict replay campaigns:
  - Initial diagnostic campaign: `validation/results/strict_replay_campaign_20260220T114632.json`
  - Final accepted campaign: `validation/results/strict_replay_campaign_20260220T121754.json`
- Strict replay summaries:
  - `validation/results/strict_replay_summary_20260220T114632.md`
  - `validation/results/strict_replay_summary_20260220T121754.md`
- Root cause and falsification artifacts:
  - `validation/results/root_cause_dt09_20260220T121754.md`
  - `validation/results/claim_status_delta_20260220T121754.md`
  - `validation/results/falsification_results_20260220T121754.md`
- RC bundle (full strict DT locked):
  - `release/RC_CHEMOSENSE_20260220T144329/bundle_manifest.json`
  - `release/RC_CHEMOSENSE_20260220T144329/validation_results/dt_results_20260220T144220.json`

### Publishing Status
- External publishing and outreach not executed.

## 2026-02-20T20:29:01Z - External Baseline + DT-09 Semantics PRD kickoff

### Objective
- Execute IoT external-baseline wave with explicit payload-economics evidence.
- Ensure DT-09 latency gate semantics are non-masked (python/native independently evaluated).

### Atomic Steps and Gates
1. Gate A: Baseline freeze + strict replay capture.
2. Gate B: External baseline comparator rerun with payload framing economics.
3. Gate C: DT-09 semantics recheck and code/test hardening (`no min(py,native)`).
4. Gate D: Strict replay campaign rerun (`>=5` consecutive runs).
5. Gate E: Packaging evidence and claim delta publication.

### Rollback/Stop Conditions
- Stop if strict replay campaign stability degrades versus baseline.
- Stop if any critical DT regression appears.
- Keep threshold constants unchanged unless a separately ratified evidence note is appended.
- Keep claims at prior tier until new evidence artifacts exist and all hard gates pass.

## 2026-02-20T21:21:03Z - External Baseline + DT-09 execution closure

### Gate Results
- Gate A (baseline freeze + strict capture): PASS
- Gate B (external comparators + payload economics): PASS
- Gate C (DT-09 non-masked semantics): PASS
- Gate D (strict replay >=5): PASS (5/5)
- Gate E (packaging + claim delta): PASS

### Key Evidence
- `/Users/zer0pa-build/ZPE IoT/zpe-iot/validation/results/2026-02-20_iot_external_baseline_dt09/dt09_semantics_recheck.json`
- `/Users/zer0pa-build/ZPE IoT/zpe-iot/validation/results/2026-02-20_iot_external_baseline_dt09/gateD_strict_replay.json`
- `/Users/zer0pa-build/ZPE IoT/zpe-iot/validation/results/2026-02-20_iot_external_baseline_dt09/iot_external_baseline_results.json`
- `/Users/zer0pa-build/ZPE IoT/zpe-iot/validation/results/2026-02-20_iot_external_baseline_dt09/claim_status_delta.md`

### Notes
- DT-09 now uses explicit native-required gate semantics when native path is available.
- Python latency remains diagnostic and cannot mask native regressions.
- External comparator artifact includes transport payload bytes and relative reduction vs raw for zpe/zstd/lz4/zlib/gorilla.

## 2026-02-21T02:19:06Z - Augmented PRD execution kickoff (A0..A7)

### Scope and governance
- PRD: `/Users/zer0pa-build/ZPE IoT/zpe-iot/docs/PRD_IOT_EXTERNAL_BASELINE_AND_DT09_2026-02-20.md`
- Scope: `/Users/zer0pa-build/ZPE IoT/zpe-iot` only.
- No threshold relaxation; evidence-first claim updates only.

### Gate order
1. A0 baseline freeze + strict replay snapshot.
2. A1 comparator normalization.
3. A2 DT-09 semantics split evidence.
4. A3 pcodec head-to-head.
5. A4 TSBS workload benchmark.
6. A5 RLE post-pass ablation + regression sweep.
7. A6 path portability audit + reproducibility fixes.
8. A7 strict replay rerun + claim packaging.

### IMP policy
- If external resource/tooling is infeasible, classify as IMP-LICENSE / IMP-ACCESS / IMP-COMPUTE / IMP-STORAGE / IMP-NOCODE with command and stderr proof.
