# Phase 2 Workstream Recheck

## Scope

Recheck the previously rejected packet-wrapper uplift candidates after repairing the native packet boundary. The question for this pass was narrow: do WI-1 and ZH-1 still fail for both parity and monotonicity, or has the rejection surface collapsed to `DT-10` only?

## What Changed

- `python/zpe_iot/_native.py` now applies the same WI-1 and ZH-1 wrapper logic as `python/zpe_iot/codec.py`.
- Native decode and sample-count parsing now unwrap experimental outer layers before reading the transport header.
- Wrapped-path coverage was added in `python/tests/test_native.py` and `python/tests/test_parity.py`.

## Validation Surface

- Targeted parity suite: `pytest -q python/tests/test_native.py python/tests/test_parity.py --no-cov` -> `11 passed`
- Direct `DT-11` reruns:
  - `ZPE_IOT_WI1_ENTROPY_STAGE=1` -> `[PASS] 100 vectors bit-identical`
  - `ZPE_IOT_ZH1_DERIVATIVE_STAGE=1` -> `[PASS] 100 vectors bit-identical`

## Post-Repair Ablation Results

### WI-1

- Artifact: `validation/results/wi1_ablation_20260320T204352.json`
- Mean baseline CR: `4.39474579531047x`
- Mean candidate CR: `6.619659634415909x`
- Mean CR gain: `50.62667882814955%`
- Mean NRMSE delta: `0.0`
- Retained: `false`
- Introduced strict failure(s): `DT-10` only

### ZH-1

- Artifact: `validation/results/zh1_ablation_20260320T210604.json`
- Mean baseline CR: `4.39474579531047x`
- Mean candidate CR: `4.777133014284905x`
- Mean CR gain: `8.701008813353232%`
- Mean NRMSE delta: `0.0`
- Retained: `false`
- Introduced strict failure(s): `DT-10` only

## Monotonicity Probe

- Artifact: `proofs/artifacts/PHASE2_MONOTONICITY_PROBE_20260320.json`
- WI-1 `DT-10` break: threshold `0.1 -> 0.2`, CR `11.554301833568406 -> 11.393602225312934`
- ZH-1 `DT-10` breaks:
  - threshold `0.1 -> 0.2`, CR `8.825208726097495 -> 8.794417606011809`
  - threshold `0.2 -> 0.5`, CR `8.794417606011809 -> 8.74512943688284`
- The probe also shows that for both workstreams, the full-stream wrapped packet grows from threshold `0.1` to `0.2` across zlib levels `1` through `9`.

## Verdict

The native parity problem is repaired. That changes the status of WI-1 and ZH-1 materially: they are no longer mixed `DT-10` plus `DT-11` failures, and are now cleanly `DT-10`-only failures.

That does not make them retained candidates. Under the current contract, a single introduced mandatory DT failure is enough to reject the workstream. The monotonicity inversion also survives simple zlib-level retuning, so the next honest move is not more wrapper tuning. Carry these workstreams forward only if Phase 2 produces a redesign that restores monotone threshold response on the strict surface.
