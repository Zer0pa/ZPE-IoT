# V6 Authority Surface — Completion Report

**Repo:** ZPE-IoT
**Agent:** Codex
**Date:** 2026-04-14
**Branch:** campaign/v6-authority-surface

## Dimensions Executed

- [x] **A: Key Metrics** — rewritten to the strongest March authority metrics with named competitor baselines
- [x] **B: Competitive Benchmarks** — added with retained dataset receipts and explicit DS-12 loss disclosure
- [x] **C: pip Install Fix** — added root-level `pyproject.toml` and verified clone-root installation/import
- [x] **D: Publish Workflow** — added `.github/workflows/publish.yml`; existing `release.yml` demoted from automatic tag publish to avoid duplicate release execution
- [x] **E: Proof Sync** — synced 3 retained March authority JSON receipts into the public repo tree

## Verification

- pip install from root: PASS
- import test: PASS
- Proof anchors verified: 3/3 exist
- Competitive claims honest: YES

## Key Metrics Written

| Metric | Value | Baseline | Proof File |
|--------|-------|----------|------------|
| COMPRESSION | 17.163613932777356× | vs zstd 1.05–5.83×, zlib 1.05–7.02× | `validation/results/bench_summary_E1_real_public_20260321T225305.json` |
| E1_WINS | 10/11 | 11-dataset benchmark | `validation/results/bench_summary_E1_real_public_20260321T225305.json` |
| DT_PASS | 27/27 | strict determinism | `validation/results/dt_results_20260321T225304.json` |
| PREFLIGHT | 94.4% (17/18) | managed preflight | `validation/results/release_preflight_report_20260321T205127.json` |

## Issues / Blockers

NONE
