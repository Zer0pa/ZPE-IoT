# ZPE-IoT: Cut Your IoT Data Costs by 80%

## The Problem
Every IoT device transmitting over cellular pays $0.50-$2.00/MB.
At 10,000 devices × 1 MB/day, that's $1.8M-$7.3M/year in data costs alone.

## The Solution
ZPE-IoT compresses sensor data 5-10x using geometric encoding.
No GPU. No cloud. Runs on ESP32, STM32, nRF, RISC-V.

## Proven Results
See `docs/BENCHMARKS.md` for latest benchmark tables and replication commands.

## How It Works
1. `pip install zpe-iot` (or link C library to firmware)
2. `compressed = zpe_iot.encode(sensor_data, preset="vibration")`
3. Send compressed bytes instead of raw data
4. Receiver runs `zpe_iot.decode(compressed)`

## Pricing
| Tier | Price | Includes |
|------|-------|----------|
| Free | $0 | Core SDK, CLI, evaluation workflows |
| Pro | $25K-$100K/year | Full presets, tuning tools, support |
| Embedded | Per-unit royalty | Certified library + integration support |

## Next Step
`pip install zpe-iot`
Try it on your data in 5 minutes.
