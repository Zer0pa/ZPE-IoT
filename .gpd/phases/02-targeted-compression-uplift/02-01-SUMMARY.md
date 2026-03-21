# Plan 02-01 Summary

## Result

- Repaired the native packet boundary in `python/zpe_iot/_native.py` so flagged WI-1 and ZH-1 packets are wrapped and unwrapped identically to the Python path.
- Added wrapped parity and sample-count coverage in `python/tests/test_native.py` and `python/tests/test_parity.py`.
- Wrote the monotonicity probe at `validation/benchmarks/phase2_monotonicity_probe.py` and persisted `proofs/artifacts/PHASE2_MONOTONICITY_PROBE_20260320.json`.
- Wrote the bounded recheck report at `proofs/artifacts/PHASE2_WORKSTREAM_RECHECK_20260320.md`.

## Key Findings

- Wrapped parity is repaired: `pytest -q python/tests/test_native.py python/tests/test_parity.py --no-cov` now passes with `11 passed`.
- `DT-11` now passes for both `ZPE_IOT_WI1_ENTROPY_STAGE=1` and `ZPE_IOT_ZH1_DERIVATIVE_STAGE=1`.
- `WI-1` still improves mean CR from `4.39474579531047x` to `6.619659634415909x`, but its post-repair ablation still rejects the candidate because the only introduced strict failure is `DT-10`.
- `ZH-1` still improves mean CR from `4.39474579531047x` to `4.777133014284905x`, but its post-repair ablation also rejects the candidate because the only introduced strict failure is `DT-10`.
- The monotonicity probe shows the full-stream wrapped packet grows from threshold `0.1` to `0.2` for both WI-1 and ZH-1 across zlib levels `1` through `9`, so simple compression-level retuning does not rescue `DT-10`.

## Durable Outputs

- `python/zpe_iot/_native.py`
- `python/tests/test_native.py`
- `python/tests/test_parity.py`
- `validation/benchmarks/phase2_monotonicity_probe.py`
- `proofs/artifacts/PHASE2_MONOTONICITY_PROBE_20260320.json`
- `proofs/artifacts/PHASE2_WORKSTREAM_RECHECK_20260320.md`

## Carry-Forward

- Phase 2 should treat WI-1 and ZH-1 as `DT-10`-only failures, not as unresolved parity problems.
- Phase 2 should not spend more time on zlib-level retuning for these two wrapper families.
- The next honest uplift task is either a monotone redesign of the transport-stage idea or a pivot to a different algorithmic family that can still move the E1 authority metric.

```yaml
gpd_return:
  status: completed
  files_written:
    - python/zpe_iot/_native.py
    - python/tests/test_native.py
    - python/tests/test_parity.py
    - validation/benchmarks/phase2_monotonicity_probe.py
    - proofs/artifacts/PHASE2_MONOTONICITY_PROBE_20260320.json
    - proofs/artifacts/PHASE2_WORKSTREAM_RECHECK_20260320.md
    - .gpd/phases/02-targeted-compression-uplift/02-01-SUMMARY.md
  issues: []
  next_actions:
    - Design a Phase 2 follow-on that either proves a monotone transport-stage redesign or pivots to a different uplift family.
    - Keep WI-1 and ZH-1 rejected until DT-10 stays green on the strict surface.
```
