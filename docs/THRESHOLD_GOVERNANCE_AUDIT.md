# Threshold Governance Audit (2026-02-14C)

This table is the single local audit map for falsification/benchmark gate thresholds.

| Threshold | Value | PRD Source | Code Source | Status |
|---|---:|---|---|---|
| `MAX_NRMSE` | `0.05` | `ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md:579` | `validation/destruct_tests/thresholds.py:6`, consumed by `validation/destruct_tests/dt01_fidelity.py:45` | Aligned |
| `MAX_NRMSE_NOISY` (default) | `0.08` | `ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md:580` | `validation/destruct_tests/thresholds.py:7`, consumed by `validation/destruct_tests/dt04_noise_robustness.py:47` | Aligned |
| `MAX_NRMSE_NOISY` (`DS-03` calibrated) | `0.12` | Ratified in PRD Addendum v1.3 §16.2 | `validation/destruct_tests/thresholds.py:9`, consumed by `validation/destruct_tests/dt04_noise_robustness.py:47` | Ratified |
| `MAX_NRMSE_NOISY` (`DS-08` calibrated) | `0.14` | Ratified in PRD Addendum v1.3 §16.2 | `validation/destruct_tests/thresholds.py:10`, consumed by `validation/destruct_tests/dt04_noise_robustness.py:47` | Ratified |
| `ADAPTIVE_THR_MIN` | `0.001` | `ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md:567` | `validation/destruct_tests/thresholds.py:13`, consumed by `validation/destruct_tests/dt15_adaptive_stability.py:24` | Aligned |
| `ADAPTIVE_THR_MAX` | `1.0` | `ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md:568` | `validation/destruct_tests/thresholds.py:14`, consumed by `validation/destruct_tests/dt15_adaptive_stability.py:24` | Aligned |
| `PRESET_MIN_MEAN_CR` | `3.8` | Ratified in PRD Addendum v1.3 §16.2 | `validation/destruct_tests/thresholds.py:16`, consumed by `validation/destruct_tests/dt12_preset_coverage.py:44` | Ratified |
| `PRESET_MAX_MEAN_NRMSE` | `0.05` | `ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md:579` | `validation/destruct_tests/thresholds.py:17`, consumed by `validation/destruct_tests/dt12_preset_coverage.py:44` | Aligned |
| `BENCHMARK_REGRESSION_MAX_DEGRADATION` | `0.05` | `ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md:508` | `validation/destruct_tests/thresholds.py:19`, consumed by `validation/destruct_tests/dt16_benchmark_regression.py:103` | Aligned |
| `WI1_MIN_CR_GAIN` | `0.12` | `ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md:968` | `validation/destruct_tests/thresholds.py:20`, consumed by `validation/destruct_tests/dt20_workstream_ablation.py:13` | Aligned |
| `ZH1_MIN_CR_GAIN` | `0.08` | `ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md:1063` | `validation/destruct_tests/thresholds.py:21`, used by `validation/benchmarks/run_zh1_ablation.py` | Aligned |

## Baseline Integrity Linkage

- Immutable baseline contract:
  - `validation/results/baseline/draconian_20260214C/bench_summary.json`
  - `validation/results/baseline/draconian_20260214C/manifest.json`
  - `validation/results/baseline/ACTIVE_BASELINE_TAG`
- Enforcement point: `validation/destruct_tests/dt16_benchmark_regression.py`.
