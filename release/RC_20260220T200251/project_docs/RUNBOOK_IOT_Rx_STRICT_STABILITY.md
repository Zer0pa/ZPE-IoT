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
