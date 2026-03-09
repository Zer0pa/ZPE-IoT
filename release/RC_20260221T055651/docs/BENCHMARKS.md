# ZPE-IoT Benchmark Results

## Evidence Labeling
- Evidence Class: **E1**
- PT-6 FINAL (E1): **PASS** (6/8 wins)
- PT-6 PROVISIONAL (E0): **NOT_AVAILABLE** (0/0 wins)

## Methodology
- Benchmarks run on DS-01..DS-08 with identical raw float64 inputs for all compressors.
- Comparators: zstd(level=3), LZ4, zlib(level=6), Gorilla-proxy.
- Fidelity metric in benchmark table: `NRMSE(window-normalized)`
- Encode/decode pathway: `zpe:encode_to_packet_bytes_then_decode_from_packet_bytes; baselines:compress_raw_bytes_then_decompress_raw_bytes`
- Iterations: 5 (warmup 1)
- Overall summary artifact: `validation/results/bench_summary_20260221T051555.json`
- E0 summary artifact: `validation/results/bench_summary_E0_proxy_20260221T051555.json`
- E1 summary artifact: `validation/results/bench_summary_E1_real_public_20260221T051555.json`
- E2 summary artifact: `validation/results/bench_summary_E2_real_customer_20260221T051555.json`

## Results Summary
- Mean zpe-iot CR across DS-01..DS-08: **4.37x**
- Active claim tier mean CR (E1): **4.37x**

## Detailed Results

| Dataset | Evidence | zpe-iot CR | zpe-iot NRMSE(window-normalized) | zstd CR | LZ4 CR | zlib CR | Gorilla CR | Winner |
|---|---|---:|---:|---:|---:|---:|---:|---|
| DS-01 | E1 | 3.99 | 0.0029 | 4.07 | 2.49 | 4.26 | 4.17 | competitor |
| DS-02 | E1 | 4.05 | 0.0151 | 1.70 | 1.59 | 1.69 | 1.68 | zpe-iot |
| DS-03 | E1 | 4.99 | 0.0060 | 3.75 | 2.33 | 3.81 | 1.64 | zpe-iot |
| DS-04 | E1 | 4.58 | 0.0440 | 1.05 | 1.00 | 1.05 | 1.04 | zpe-iot |
| DS-05 | E1 | 4.58 | 0.0041 | 5.83 | 2.91 | 7.02 | 6.22 | competitor |
| DS-06 | E1 | 4.09 | 0.3175 | 2.93 | 1.84 | 2.92 | 2.99 | zpe-iot |
| DS-07 | E1 | 4.54 | 0.0174 | 1.37 | 1.25 | 1.37 | 1.22 | zpe-iot |
| DS-08 | E1 | 4.14 | 0.0299 | 3.57 | 2.12 | 3.55 | 2.72 | zpe-iot |

### Charts
![CR comparison](benchmarks/cr_comparison.png)
![Pareto frontier](benchmarks/pareto_frontier.png)
![Latency comparison](benchmarks/latency_comparison.png)
![Memory comparison](benchmarks/memory_comparison.png)

## Reproducibility Envelope
- Dataset manifest SHA256: `48256bed9307af723a01c8f4bb4fd3422361afeff7a94de3512ccad3fdc6839e`
- Toolchain: `{"cargo": "cargo 1.90.0 (840b83a10 2025-07-30)", "lz4": "4.4.5", "numpy": "2.4.2", "python": "3.14.0", "zstandard": "0.25.0"}`
- Hardware profile: `{"machine": "x86_64", "platform": "macOS-15.5-x86_64-i386-64bit-Mach-O", "processor": "i386"}`
- Commands: `{"comparators": ["python validation/benchmarks/bench_vs_zstd.py", "python validation/benchmarks/bench_vs_lz4.py", "python validation/benchmarks/bench_vs_zlib.py", "python validation/benchmarks/bench_vs_gorilla.py"], "run_benchmarks": "python validation/benchmarks/run_benchmarks.py"}`

## When NOT to Use ZPE-IoT
- Already compressed payloads.
- Cryptographically random/high-entropy data.
- Workloads demanding strict lossless reconstruction.

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
