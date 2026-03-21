<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# ZPE-IoT Benchmark Results

<p>
  <img src="../.github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

| Field | Current truth |
|---|---|
| Evidence class | `E1` |
| Active dataset surface | `DS-01..DS-10`, `DS-12` |
| Blocked dataset | `DS-11` |
| PT-6 final | `PASS (10/11 wins)` |
| Mean CR | `17.163613932777356x` |
| Active summary artifact | `validation/results/bench_summary_E1_real_public_20260321T225305.json` |
| E2 status | `NOT_AVAILABLE` |

<p>
  <img src="../.github/assets/readme/section-bars/evidence.svg" alt="EVIDENCE" width="100%">
</p>

- Benchmarks run on 11 real-public READY datasets with identical raw float64 inputs for all compressors.
- Comparators: zstd(level=3), LZ4, zlib(level=6), Gorilla-proxy.
- Fidelity metric in the table: `NRMSE(window-normalized)`.
- Encode/decode pathway: `zpe:encode_to_packet_bytes_then_decode_from_packet_bytes; baselines:compress_raw_bytes_then_decompress_raw_bytes`.
- Iterations: 5 (warmup 1).
- Overall summary artifact: `validation/results/bench_summary_20260321T225305.json`.
- E0 summary artifact: `validation/results/bench_summary_E0_proxy_20260321T225305.json`.
- E1 summary artifact: `validation/results/bench_summary_E1_real_public_20260321T225305.json`.
- E2 summary artifact: `validation/results/bench_summary_E2_real_customer_20260321T225305.json`.

## Detailed Results

| Dataset | Evidence | zpe-iot CR | zpe-iot NRMSE(window-normalized) | zstd CR | LZ4 CR | zlib CR | Gorilla CR | Winner |
|---|---|---:|---:|---:|---:|---:|---:|---|
| DS-01 | E1 | 6.18 | 0.0029 | 4.07 | 2.49 | 4.26 | 4.17 | zpe-iot |
| DS-02 | E1 | 6.40 | 0.0151 | 1.70 | 1.59 | 1.69 | 1.68 | zpe-iot |
| DS-03 | E1 | 7.66 | 0.0060 | 3.75 | 2.33 | 3.81 | 1.64 | zpe-iot |
| DS-04 | E1 | 7.16 | 0.0440 | 1.05 | 1.00 | 1.05 | 1.04 | zpe-iot |
| DS-05 | E1 | 7.29 | 0.0041 | 5.83 | 2.91 | 7.02 | 6.22 | zpe-iot |
| DS-06 | E1 | 6.24 | 0.3175 | 2.93 | 1.84 | 2.92 | 2.99 | zpe-iot |
| DS-07 | E1 | 6.98 | 0.0174 | 1.37 | 1.25 | 1.37 | 1.22 | zpe-iot |
| DS-08 | E1 | 6.57 | 0.0299 | 3.57 | 2.12 | 3.55 | 2.72 | zpe-iot |
| DS-09 | E1 | 6.38 | 0.0055 | 2.55 | 1.55 | 2.43 | 1.06 | zpe-iot |
| DS-10 | E1 | 7.47 | 0.0923 | 1.91 | 1.81 | 1.91 | 1.86 | zpe-iot |
| DS-12 | E1 | 120.47 | 0.0000 | 5957.82 | 234.06 | 879.68 | 814.11 | competitor |

### Charts
![CR comparison](benchmarks/cr_comparison.png)
![Pareto frontier](benchmarks/pareto_frontier.png)
![Latency comparison](benchmarks/latency_comparison.png)
![Memory comparison](benchmarks/memory_comparison.png)

<p>
  <img src="../.github/assets/readme/section-bars/open-risks-non-blocking.svg" alt="OPEN RISKS (NON-BLOCKING)" width="100%">
</p>

| Boundary | Current truth |
|---|---|
| `DS-11` | Explicitly `BLOCKED` and excluded from the active E1 authority surface |
| `DS-12` | Competitor win on the current E1 real-public surface |
| E2 | No active real-customer claim tier is promoted |
| Fit | ZPE-IoT is not a strict lossless codec and is not a fit for already-compressed or cryptographically random payloads |

<p>
  <img src="../.github/assets/readme/section-bars/running-the-test-suite.svg" alt="RUNNING THE TEST SUITE" width="100%">
</p>

## Reproducibility Envelope

- Dataset manifest SHA256: `64f004cfac32a0f48303b4eadaca680ed95abb93a652ebf4653f0fa16858f24c`
- Toolchain: `{"cargo": "cargo 1.90.0 (840b83a10 2025-07-30)", "lz4": "4.4.5", "numpy": "2.4.3", "python": "3.14.0", "zstandard": "0.25.0"}`
- Hardware profile: `{"machine": "arm64", "platform": "macOS-15.5-arm64-arm-64bit-Mach-O", "processor": "arm"}`
- Commands: `{"comparators": ["python validation/benchmarks/bench_vs_zstd.py", "python validation/benchmarks/bench_vs_lz4.py", "python validation/benchmarks/bench_vs_zlib.py", "python validation/benchmarks/bench_vs_gorilla.py"], "run_benchmarks": "python validation/benchmarks/run_benchmarks.py"}`

## How to Reproduce

```bash
ZPE_IOT_ROOT="${ZPE_IOT_ROOT:-$(pwd)}"
cd "$ZPE_IOT_ROOT"
source .venv/bin/activate
python validation/benchmarks/run_benchmarks.py
python validation/benchmarks/generate_report.py
python validation/benchmarks/run_wi1_ablation.py --repeats 5
python validation/benchmarks/run_zh1_ablation.py --repeats 5
```
