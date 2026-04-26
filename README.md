[![CI](https://github.com/Zer0pa/ZPE-IoT/actions/workflows/ci.yml/badge.svg)](https://github.com/Zer0pa/ZPE-IoT/actions/workflows/ci.yml)
<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# ZPE-IoT

**Deterministic bounded-lossy sensor compression — 6.83x mean vs zstd 2.87x across 10 real public datasets (E1 benchmark, 10/10 wins on DS-01..DS-10; DS-12 is a separate competitor win — see disclosure below). Bounded-lossy vs lossless.**

[Architecture](docs/ARCHITECTURE.md) | [API](docs/API.md) | [Benchmarks](proofs/artifacts/public_benchmarks/INDEX.json) | [Package](python/README.md) | [Legal](docs/LEGAL_BOUNDARIES.md)

SAL v7.0 — free below $100M annual revenue. See [LICENSE](LICENSE).

---

## What This Is

ZPE-IoT is a deterministic sensor compression SDK for constrained telemetry streams. The repo ships a Rust core with PyO3 bindings, an installable Python package, committed benchmark receipts, and the validation scripts used to keep that surface honest.

This README is intentionally narrower than the March audit packet. Claims stay only where this repo has both committed proof artifacts and a CI check that exercises the relevant surface.

## CI-Backed Surface

The default CI workflow currently checks:

- Rust tests plus `cargo clippy -D warnings`
- editable install, wheel build, and Python test matrix on Ubuntu and macOS for CPython 3.10-3.12
- provenance smoke over the committed dataset manifest and transformed artifacts, plus DT-18 strict-gate enforcement
- public benchmark receipt sanity against the committed E1 benchmark summary and receipt index
- security scan plus release-manifest generation scripts

Source workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

## Public Benchmark Snapshot

**Framing disclosure:** ZPE-IoT is a bounded-lossy codec. All E1 comparators (zstd, lz4, zlib, gorilla) are lossless — compression-ratio comparisons are informative but not apples-to-apples. DS-12 is the explicit case where the comparator surface wins.

The committed E1 public benchmark surface reports a 10/11 win split for ZPE-IoT across DS-01..DS-10 plus DS-12.

| Slice | Current committed receipt |
|------|----------------------------|
| E1 wins | 10 / 11 |
| DS-01..DS-10 mean compression | 6.83x |
| DS-01..DS-10 mean zstd compression | 2.87x |
| DS-12 | competitor win |
| DS-05 | ZPE-IoT win (7.29x) with narrow margin over zlib (7.02x) |

Sources:

- [`validation/results/bench_summary_E1_real_public_20260321T225305.json`](validation/results/bench_summary_E1_real_public_20260321T225305.json)
- [`proofs/artifacts/public_benchmarks/INDEX.json`](proofs/artifacts/public_benchmarks/INDEX.json)
- [`proofs/artifacts/public_benchmarks/DS-05.json`](proofs/artifacts/public_benchmarks/DS-05.json)
- [`proofs/artifacts/public_benchmarks/DS-12.json`](proofs/artifacts/public_benchmarks/DS-12.json)

## Comp Benchmarks vs Prior Art

All comparisons below are drawn from committed E1 receipts run on the same 10 real public datasets (DS-01..DS-10). Baselines are lossless; ZPE-IoT is bounded-lossy. NRMSE is window-normalized. Latency is per-window encode at the native (Rust) layer.

**Per-comparator win count (DS-01..DS-10, 10 datasets):**

| Comparator | ZPE-IoT wins | ZPE-IoT mean CR | Comparator mean CR |
|---|---|---|---|
| zstd | 10 / 10 | 6.83x | 2.87x |
| lz4 | 10 / 10 | 6.83x | 1.89x |
| zlib | 10 / 10 | 6.83x | 3.00x |
| gorilla | 10 / 10 | 6.83x | 2.46x |

**Structural highlight — high-entropy accelerometer (DS-04, UCI HAR body_acc_x):**

On high-entropy inertial signals, lossless codecs approach break-even or below, while ZPE-IoT's bounded-lossy design continues to compress:

| Codec | Compression ratio |
|---|---|
| ZPE-IoT | **7.16x** |
| zstd | 1.05x |
| lz4 | ~1.00x (break-even) |
| zlib | 1.05x |
| gorilla | 1.04x |

Source: [`proofs/artifacts/public_benchmarks/DS-04.json`](proofs/artifacts/public_benchmarks/DS-04.json) + CI job `benchmark_sanity` in [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

**GPS trajectory (DS-07, UCI GPS Trajectories):**

| Codec | Compression ratio |
|---|---|
| ZPE-IoT | **6.98x** |
| zstd | 1.37x |
| zlib | 1.37x |
| gorilla | 1.22x |

Source: [`proofs/artifacts/public_benchmarks/DS-07.json`](proofs/artifacts/public_benchmarks/DS-07.json)

**Per-preset compression ratios (DT-12, committed CI result):**

| Preset | Mean CR | Mean NRMSE (window-norm) |
|---|---|---|
| temperature | 8.03x | 0.0074 |
| gps_track | 7.80x | 0.0191 |
| pressure | 7.29x | 0.0041 |
| accelerometer | 7.12x | 0.0397 |
| flow | 8.03x | 0.0074 |
| voltage | 6.60x | 0.0283 |
| current | 6.60x | 0.0283 |
| vibration | 6.40x | 0.0151 |
| generic | 6.24x | 0.0020 |

Source: [`validation/results/dt_results_20260321T225304.json`](validation/results/dt_results_20260321T225304.json) (DT-12) + CI job `strict_dt_smoke`

## Latency and Throughput

Committed DT-09 result (per-window encode/decode, 256-sample window):

| Layer | Mean latency | p99 latency |
|---|---|---|
| Native (Rust) | 0.031 ms | 0.035 ms |
| Python (PyO3) | 0.723 ms | 0.789 ms |
| Threshold gate | mean < 0.500 ms | p99 < 2.000 ms |

Committed DT-07 result: 10 million samples encoded in 0.30 s (latch-freedom check, no queue buildup).

Sources: [`validation/results/dt_results_20260321T225304.json`](validation/results/dt_results_20260321T225304.json) (DT-07, DT-09) + CI job `strict_dt_smoke`

## What We Don't Claim

- no universal compressor dominance
- no lossless reconstruction
- no production protocol bridge beyond the published package surface
- no CI-backed claim about live PyPI publication state
- no CI-backed claim that the raw public dataset mirror is present on every clean checkout

## Quick Start

**Install from source:**

```bash
git clone https://github.com/Zer0pa/ZPE-IoT zpe-iot
cd zpe-iot
python -m pip install -e './python[dev]'
cargo test --manifest-path core/Cargo.toml --release
python -m pytest python/tests -v
```

**Run the benchmark receipt sanity check:**

```bash
python validation/benchmarks/export_public_benchmarks.py
```

## Repo Shape

| Area | Purpose |
|---|---|
| `README.md`, `pyproject.toml`, `LICENSE` | repo front door and package metadata |
| `core/` | canonical Rust codec kernel and Rust test surface |
| `python/` | installable Python package and CLI |
| `docs/` | architecture, API, integration, and legal docs |
| `proofs/` | committed public benchmark receipts and related proof routing |
| `validation/` | datasets, destructive tests, benchmark scripts, and result artifacts |

## Docs and Support

| Route | Target |
|---|---|
| Architecture | `docs/ARCHITECTURE.md` |
| API and CLI | `docs/API.md`, `docs/CLI_CONTRACT.md` |
| Benchmark authority | `proofs/artifacts/public_benchmarks/INDEX.json` |
| Legal boundary | `docs/LEGAL_BOUNDARIES.md` |
| Integration guidance | `docs/INTEGRATION_GUIDE.md` |
| Security reporting | `SECURITY.md` |

## Portfolio Position

ZPE-IoT is the constrained-telemetry lane in the [Zer0pa ZPE](https://github.com/Zer0pa) codec portfolio — one of 17 independent domain-specific encoding products, each with its own proof surface, sharing a license but not a shared platform.

## Upcoming Workstreams

This section captures the active lane priorities — what the next agent or contributor picks up, and what investors should expect. Cadence is continuous, not milestoned.

- **Production protocol bridge** — Active Engineering. Pick one of MQTT, Kafka, or SparkplugB; ship a thin adapter (encoder reads from broker → emits zpe-iot frames → decoder publishes back). Single SDK→deployment unlock.
- **DS-12 loss diagnosis** — Research-Deferred — Investigation Underway. Profile what about DS-12 made it lose; decide whether it is a bounded-corpus exclusion (announce) or a primitive gap (close).
