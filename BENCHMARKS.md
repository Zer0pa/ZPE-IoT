# ZPE-IoT Benchmarks

This root file records the reproducibility path for the benchmark surface exposed by this repo. Current published benchmark authority lives in [docs/BENCHMARKS.md](docs/BENCHMARKS.md) and the referenced JSON artifacts under `validation/results/`.

## Scope

- Inputs: READY real-public datasets under `validation/datasets/`
- Comparators: `zlib`, `LZ4`, `zstd`, `Gorilla-proxy`
- Fidelity metric: `NRMSE(window-normalized)`
- Fairness envelope: ZPE encodes to wire bytes; baselines compress raw float64 bytes

## Methodology

1. Verify dataset provenance against `validation/datasets/manifest.json`.
2. Load READY datasets through `validation.datasets.loader`.
3. Run dataset-specific presets from `validation/benchmarks/_common.py`.
4. Execute comparator harnesses for `zlib`, `LZ4`, `zstd`, and Gorilla-proxy.
5. Aggregate outputs into split summaries and render the benchmark report bundle.

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
- Dataset manifest: `validation/datasets/manifest.json`
