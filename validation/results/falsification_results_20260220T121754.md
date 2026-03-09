# Falsification Results (20260220T121754)

## Campaign Under Test
- Command: `python validation/destruct_tests/run_all_dts.py --strict-gates`
- Environment: pinned interpreter `.venv/bin/python`
- Repeats: 5 consecutive full strict runs
- Artifact: `validation/results/strict_replay_campaign_20260220T121754.json`

## Outcomes
- Strict mandatory gates:
  - Runs passing strict: 5/5
  - Mandatory failures observed: 0
  - `results_count`: 27 on every run
- DT-09 falsification:
  - No threshold violations in final campaign.
  - Observed max values: mean=0.463ms, p99=1.884ms (both below gate limits).
- DT-10 / DT-11 falsification:
  - PASS on all 5 runs.
- Modality isolation falsification:
  - DT-22 PASS on all 5 runs.
  - DT-27 PASS on all 5 runs (no cross-modality false-positive decode acceptance).

## RC Evidence Selection Falsification
- RC bundle now rejects non-full strict DT evidence by construction in `scripts/build_chemosense_rc_bundle.py`.
- Regression test coverage:
  - `python/tests/test_chemosense_rc_bundle_strict.py`
  - Verifies acceptance of latest full strict DT and rejection when no full strict DT exists.

## Conclusion
- No surviving local falsifiers in this scope after hardening delta.
