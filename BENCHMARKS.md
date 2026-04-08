# ZPE-IoT Benchmarks

This root file records the reproducibility path for the benchmark surface exposed by this repo. [docs/BENCHMARKS.md](docs/BENCHMARKS.md) remains the front-door summary surface. This file is the operator-grade Phase 3 table view for the same E1 dataset tier.

## Scope

- Inputs: READY real-public datasets under `validation/datasets/`
- Comparators: `zlib`, `LZ4`, `zstd`, `Gorilla-proxy`
- Fidelity metric: `NRMSE(window-normalized)`
- Fairness envelope: ZPE encodes to wire bytes; baselines compress identical raw float64 payloads

## Methodology

1. Verify dataset provenance against `validation/datasets/manifest.json`.
2. Load READY datasets through `validation.datasets.loader`.
3. Run dataset-specific presets from `validation/benchmarks/_common.py`.
4. Execute comparator harnesses for `zlib`, `LZ4`, `zstd`, and Gorilla-proxy`.
5. Aggregate outputs into split summaries and compare the rerun against the promoted E1 authority artifact.

## Reproducibility

```bash
python validation/benchmarks/run_benchmarks.py
python validation/benchmarks/generate_report.py
python validation/benchmarks/run_wi1_ablation.py --repeats 5
python validation/benchmarks/run_zh1_ablation.py --repeats 5
```

## Current Authority Inputs

- Current docs view: `docs/BENCHMARKS.md`
- Promoted E1 summary on `main`: `validation/results/bench_summary_E1_real_public_20260321T225305.json`
- Phase 3 verification rerun: `validation/results/bench_summary_E1_real_public_20260408T043806.json`
- Rerun match: identical `10/11` wins, identical `17.163613932777356x` mean CR, identical dataset rows
- Dataset manifest: `validation/datasets/manifest.json`

## Detailed Results

| Dataset | Domain | Raw bytes | ZPE bytes | ZPE CR | Fidelity (NRMSE) | Source |
|---|---|---:|---:|---:|---:|---|
| DS-01 | air quality | 358,400 | 57,950 | 6.18x | 0.0029 | UCI AirQuality (CO channel) |
| DS-02 | bearing vibration | 163,840 | 25,620 | 6.40x | 0.0151 | PHM 2012 Bearing Challenge (Learning_set/Bearing1_1) |
| DS-03 | environmental sensing | 655,360 | 86,400 | 7.66x | 0.0060 | MIT Intel Lab Data (temperature) |
| DS-04 | human activity IMU | 655,360 | 92,480 | 7.16x | 0.0440 | UCI HAR Smartphone Inertial Signals (body_acc_x) |
| DS-05 | weather telemetry | 163,840 | 22,525 | 7.29x | 0.0041 | NOAA Global Hourly (station 01001099999) |
| DS-06 | urban demand telemetry | 409,600 | 65,640 | 6.24x | 0.3175 | Numenta NAB NYC Taxi |
| DS-07 | GPS trajectory | 655,360 | 95,000 | 6.98x | 0.0174 | UCI GPS Trajectories (go_track trackpoints) |
| DS-08 | household power | 655,360 | 99,780 | 6.57x | 0.0299 | UCI Household Power Consumption (Voltage channel) |
| DS-09 | bearing vibration | 655,360 | 102,735 | 6.38x | 0.0055 | CWRU Bearing Drive End 48kHz (109.mat) |
| DS-10 | human activity IMU | 655,360 | 88,305 | 7.47x | 0.0923 | UCI HAR Smartphone Inertial Signals (body_acc_x test split) |
| DS-12 | electric load | 655,360 | 5,440 | 120.47x | 0.0000 | UCI Electricity Load Diagrams (MT_001) |

## Baseline Comparison

| Dataset | Best baseline | Baseline bytes | Baseline CR | ZPE bytes | ZPE CR | Improvement vs baseline | Winner |
|---|---|---:|---:|---:|---:|---:|---|
| DS-01 | zlib | 16,880 | 4.26x | 57,950 | 6.18x | 1.45x | zpe-iot |
| DS-02 | zstd | 19,295 | 1.70x | 25,620 | 6.40x | 3.77x | zpe-iot |
| DS-03 | zlib | 34,371 | 3.81x | 86,400 | 7.66x | 2.01x | zpe-iot |
| DS-04 | zlib | 124,916 | 1.05x | 92,480 | 7.16x | 6.82x | zpe-iot |
| DS-05 | zlib | 4,667 | 7.02x | 22,525 | 7.29x | 1.04x | zpe-iot |
| DS-06 | gorilla | 27,656 | 2.99x | 65,640 | 6.24x | 2.09x | zpe-iot |
| DS-07 | zstd | 95,547 | 1.37x | 95,000 | 6.98x | 5.09x | zpe-iot |
| DS-08 | zstd | 36,692 | 3.57x | 99,780 | 6.57x | 1.84x | zpe-iot |
| DS-09 | zstd | 51,341 | 2.55x | 102,735 | 6.38x | 2.50x | zpe-iot |
| DS-10 | zstd | 68,483 | 1.91x | 88,305 | 7.47x | 3.90x | zpe-iot |
| DS-12 | zstd | 22 | 5957.82x | 5,440 | 120.47x | 0.02x | competitor |

## Dataset Sources

- DS-01: `https://archive.ics.uci.edu/ml/machine-learning-databases/00360/AirQualityUCI.zip`
- DS-02: `https://raw.githubusercontent.com/wkzs111/phm-ieee-2012-data-challenge-dataset/master/Learning_set/Bearing1_1/acc_00001.csv`
- DS-03: `https://db.csail.mit.edu/labdata/data.txt.gz`
- DS-04: `https://archive.ics.uci.edu/static/public/240/human+activity+recognition+using+smartphones.zip`
- DS-05: `https://www.ncei.noaa.gov/data/global-hourly/access/2022/01001099999.csv`
- DS-06: `https://raw.githubusercontent.com/numenta/NAB/master/data/realKnownCause/nyc_taxi.csv`
- DS-07: `https://archive.ics.uci.edu/static/public/354/gps+trajectories.zip`
- DS-08: `https://archive.ics.uci.edu/ml/machine-learning-databases/00235/household_power_consumption.zip`
- DS-09: `https://engineering.case.edu/sites/default/files/109.mat`
- DS-10: `https://archive.ics.uci.edu/static/public/240/human+activity+recognition+using+smartphones.zip`
- DS-12: `https://archive.ics.uci.edu/static/public/321/electricityloaddiagrams20112014.zip`

## EnOcean Trace Check

- Checked official EnOcean white paper and product/download surfaces for public trace material.
- Checked SmartStudio telemetry docs for downloadable sample streams.
- Result: public schema examples exist, but no freely downloadable EnOcean time-series trace corpus was found.
- Status: blocked pending a public downloadable EnOcean sensor trace dataset.
