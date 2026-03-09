# ZPE-IoT: Sensor Compression Brief (E1)

## The Problem
Every IoT device transmitting over cellular pays $0.50-$2.00/MB.
At 10,000 devices × 1 MB/day, that's $1.8M-$7.3M/year in data costs alone.

## The Solution
ZPE-IoT (E1) compresses sensor data with signal-aware geometric encoding.
No GPU. No cloud. Runs on ESP32, STM32, nRF, RISC-V.

## Proven Results
Evidence class for this brief: **(E1)** real-public datasets.
See `docs/BENCHMARKS.md` for latest benchmark tables, PT-6 FINAL/PROVISIONAL labels, and replication commands.
Current E1 snapshot (2026-03-09): mean CR **4.37x**, PT-6 FINAL **PASS** (6/8 wins), E2 claim tier **NOT_AVAILABLE** (0 datasets). Artifact: `validation/results/bench_summary_E1_real_public_20260309T060843.json`.

## How It Works
1. `python -m pip install -e ./python` for local/private evaluation (or link the C library to firmware)
2. `compressed = zpe_iot.encode(sensor_data, preset="vibration")`
3. Send compressed bytes instead of raw data
4. Receiver runs `zpe_iot.decode(compressed)`

Current limitation: public package publication has not been cleared. Use a private repo checkout or wheel for evaluation.

## Pricing
| Tier | Price | Includes |
|------|-------|----------|
| Free | $0 | Core SDK, CLI, evaluation workflows |
| Pro | $25K-$100K/year | Full presets, tuning tools, support |
| Embedded | Per-unit royalty | Certified library + integration support |

## Next Step
Run a side-by-side trial on your own telemetry:
`python scripts/customer_demo.py <your_data.csv> --preset <preset>`
