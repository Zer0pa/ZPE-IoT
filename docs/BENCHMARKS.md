# ZPE-IoT Benchmark Results

## Methodology
- Benchmarks run on DS-01..DS-08 with identical raw float64 inputs for all compressors.
- Comparators: zstd(level=3), LZ4, zlib(level=6), Gorilla-proxy.
- Latest summary artifact: `/Users/prinivenpillay/ZPE IoT/zpe-iot/validation/results/bench_summary_20260213T204926.json`

## Results Summary
- PT-6 status: **PASS** (6/8 wins for zpe-iot)
- Mean zpe-iot CR across DS-01..DS-08: **10.51x**

## Detailed Results

| Dataset | zpe-iot CR | zpe-iot NRMSE | zstd CR | LZ4 CR | zlib CR | Gorilla CR | Winner |
|---|---:|---:|---:|---:|---:|---:|---|
| DS-01 | 4.10 | 0.0155 | 1.12 | 1.00 | 1.18 | 1.17 | zpe-iot |
| DS-02 | 10.27 | 0.0029 | 10.04 | 5.94 | 8.06 | 7.70 | zpe-iot |
| DS-03 | 13.49 | 0.0178 | 19.93 | 2.94 | 11.19 | 15.26 | competitor |
| DS-04 | 5.64 | 0.0080 | 4.73 | 3.03 | 4.21 | 3.99 | zpe-iot |
| DS-05 | 20.26 | 0.0058 | 18.89 | 12.83 | 17.61 | 16.85 | zpe-iot |
| DS-06 | 17.70 | 0.0391 | 5.08 | 3.17 | 4.46 | 4.36 | zpe-iot |
| DS-07 | 7.46 | 0.0033 | 1.09 | 1.00 | 1.22 | 1.23 | zpe-iot |
| DS-08 | 5.20 | 0.0362 | 5.35 | 3.29 | 4.65 | 4.69 | competitor |

### Charts
![CR comparison](benchmarks/cr_comparison.png)
![Pareto frontier](benchmarks/pareto_frontier.png)
![Latency comparison](benchmarks/latency_comparison.png)
![Memory comparison](benchmarks/memory_comparison.png)

## When NOT to Use ZPE-IoT
- Already compressed payloads.
- Cryptographically random/high-entropy data.
- Workloads demanding strict lossless reconstruction.

## How to Reproduce
```bash
cd /Users/prinivenpillay/ZPE\ IoT/zpe-iot
source .venv/bin/activate
python validation/benchmarks/run_benchmarks.py
python validation/benchmarks/generate_report.py
```

## ROI Calculator
Example: 10,000 devices × 1 MB/day × $1.00/MB = $3.65M/year
At 5x compression: $0.73M/year
Savings: $2.92M/year; $50K license implies ~58x ROI.
