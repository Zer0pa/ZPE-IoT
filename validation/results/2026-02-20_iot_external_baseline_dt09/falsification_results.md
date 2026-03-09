# Falsification Results

- Generated: `2026-02-20T21:20:47.015514+00:00`

## Hypothesis 1: Native latency regressions can be masked by Python path
- Before evidence: `validation/results/2026-02-20_iot_external_baseline_dt09/gateA_dt09_source_before.log` (contains_min_masking=True)
- After evidence: `validation/results/2026-02-20_iot_external_baseline_dt09/gateC_dt09_source_after.log` (contains_min_masking=False)
- Regression test evidence: `validation/results/2026-02-20_iot_external_baseline_dt09/gateC_pytest_dt09_semantics.log` (PASS)
- Result: FALSIFIED (masking path removed).

## Hypothesis 2: Strict gate replay is unstable post-fix
- Replay evidence: `validation/results/2026-02-20_iot_external_baseline_dt09/gateD_strict_replay.json`
- Campaign summary: `{'total_runs': 5, 'pass_runs': 5, 'fail_runs': 0, 'all_green': True}`
- Result: FALSIFIED (5/5 strict runs PASS).

## Hypothesis 3: External comparator payload economics not captured
- Payload artifact: `validation/results/2026-02-20_iot_external_baseline_dt09/iot_external_baseline_results.json`
- Result: FALSIFIED (transport payload bytes and relative reduction rows present for zpe/zlib/lz4/zstd/gorilla).
