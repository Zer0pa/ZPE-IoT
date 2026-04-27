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

ZPE-IoT is a **bounded-lossy** codec — not a lossless compressor. It finds minimal and fundamental representations of smooth-trajectory sensor streams. It is **not** a protocol bridge, **not** a universal sensor platform, and **not** a lossless reconstruction codec.

The headline metric is **6.83× mean compression ratio** across DS-01..DS-10 (10 real public datasets, E1 benchmark) versus zstd 2.87× lossless — with 10/10 wins. On high-entropy inertial signals (DS-04), ZPE-IoT yields 7.16× where zstd reaches only 1.05×. Proof path: [`proofs/artifacts/public_benchmarks/INDEX.json`](proofs/artifacts/public_benchmarks/INDEX.json).

DS-12 is an honest exception: the comparator wins on that dataset. Production protocol bridge (MQTT/Kafka/SparkplugB) is not yet shipped — that is the active engineering focus for the next workstream.

This README stays narrower than the March audit packet. Claims stay only where this repo has both committed proof artifacts and a CI check that exercises the relevant surface.

| Field | Value |
|-------|-------|
| Architecture | SENSOR_STREAM |
| Encoding | IOT_BOUNDED_LOSSY_V1 |

---

## Key Metrics

| Metric | Value | Baseline |
|--------|-------|----------|
| COMPRESSION | 6.83× mean | vs zstd 2.87× (DS-01..DS-10) |
| E1_WINS | 10 / 10 | vs zstd, lz4, zlib, gorilla |
| DS04_HIGH_ENTROPY | 7.16× | vs zstd 1.05× (UCI HAR body_acc_x) |
| LATENCY_NATIVE | 0.031 ms mean | 256-sample window, Rust layer |

> Source: [`validation/results/bench_summary_E1_real_public_20260321T225305.json`](validation/results/bench_summary_E1_real_public_20260321T225305.json), [`proofs/artifacts/public_benchmarks/DS-04.json`](proofs/artifacts/public_benchmarks/DS-04.json), [`validation/results/dt_results_20260321T225304.json`](validation/results/dt_results_20260321T225304.json) (DT-09)

---

## Competitive Benchmarks

All comparisons below are drawn from committed E1 receipts run on the same 10 real public datasets (DS-01..DS-10). Baselines are lossless; ZPE-IoT is bounded-lossy. NRMSE is window-normalized. Latency is per-window encode at the native (Rust) layer.

**Per-comparator win count (DS-01..DS-10, 10 datasets):**

| Comparator | ZPE-IoT wins | ZPE-IoT mean CR | Comparator mean CR |
|---|---|---|---|
| **ZPE-IoT** | — | **6.83×** | — |
| zstd | 10 / 10 | 6.83× | 2.87× |
| lz4 | 10 / 10 | 6.83× | 1.89× |
| zlib | 10 / 10 | 6.83× | 3.00× |
| gorilla | 10 / 10 | 6.83× | 2.46× |

**Structural highlight — high-entropy accelerometer (DS-04, UCI HAR body_acc_x):**

On high-entropy inertial signals, lossless codecs approach break-even or below, while ZPE-IoT's bounded-lossy design continues to compress:

| Codec | Compression ratio |
|---|---|
| **ZPE-IoT** | **7.16×** |
| zstd | 1.05× |
| lz4 | ~1.00× (break-even) |
| zlib | 1.05× |
| gorilla | 1.04× |

Source: [`proofs/artifacts/public_benchmarks/DS-04.json`](proofs/artifacts/public_benchmarks/DS-04.json) + CI job `benchmark_sanity` in [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

**GPS trajectory (DS-07, UCI GPS Trajectories):**

| Codec | Compression ratio |
|---|---|
| **ZPE-IoT** | **6.98×** |
| zstd | 1.37× |
| zlib | 1.37× |
| gorilla | 1.22× |

Source: [`proofs/artifacts/public_benchmarks/DS-07.json`](proofs/artifacts/public_benchmarks/DS-07.json)

**DS-12 — honest competitor win:**

| Codec | Result |
|---|---|
| ZPE-IoT | Loss |
| Comparator | Win |

Source: [`proofs/artifacts/public_benchmarks/DS-12.json`](proofs/artifacts/public_benchmarks/DS-12.json). Investigation underway — see Upcoming Workstreams.

**Per-preset compression ratios (DT-12, committed CI result):**

| Preset | Mean CR | Mean NRMSE (window-norm) |
|---|---|---|
| temperature | 8.03× | 0.0074 |
| gps_track | 7.80× | 0.0191 |
| pressure | 7.29× | 0.0041 |
| accelerometer | 7.12× | 0.0397 |
| flow | 8.03× | 0.0074 |
| voltage | 6.60× | 0.0283 |
| current | 6.60× | 0.0283 |
| vibration | 6.40× | 0.0151 |
| generic | 6.24× | 0.0020 |

Source: [`validation/results/dt_results_20260321T225304.json`](validation/results/dt_results_20260321T225304.json) (DT-12) + CI job `strict_dt_smoke`

---

## What We Prove

- Rust core passes `cargo test --release` and `cargo clippy -D warnings` on every push (CI job: `rust_tests`)
- Python package installs as editable wheel and passes pytest matrix on Ubuntu and macOS for CPython 3.10–3.12 (CI job: `python_tests`)
- 27 deterministic tests (DT-01..DT-27) pass under strict-gate mode — no mandatory SKIP tolerated (CI job: `strict_dt_smoke`)
- E1 benchmark surface: 10/10 wins vs zstd, lz4, zlib, gorilla on DS-01..DS-10 — committed receipt sanity checked by CI (CI job: `benchmark_sanity`)
- Dataset manifest provenance and transformation hashes verified for DS-01..DS-10 and DS-12; DS-11 remains explicitly BLOCKED (CI job: `provenance_smoke`)
- DT-18 strict-gate enforcement: mandatory-SKIP paths reject in strict mode, allow in relaxed mode
- Security scan and release-manifest generation scripts pass clean (CI job: `security_scan`)
- Source workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

---

## What We Don't Claim

- no universal compressor dominance
- no lossless reconstruction
- no production protocol bridge beyond the published package surface
- no CI-backed claim about live PyPI publication state
- no CI-backed claim that the raw public dataset mirror is present on every clean checkout

---

## Commercial Readiness

| Field | Value |
|-------|-------|
| Verdict | PARTIAL |
| Commit SHA | 5b7604c |
| Source | `validation/results/release_preflight_report_20260321T205127.json` |

17/18 preflight checks PASS. D01_DEFERRED_PUBLISH is deferred pending protocol-bridge milestone. Publish pipeline infrastructure is in place (OIDC trusted publishing, PEP 740 attestations); live PyPI publication is not CI-backed at this commit.

---

## Tests and Verification

| Code | Check | Verdict |
|------|-------|---------|
| DT-01 | Fidelity Gate — NRMSE within bounds across DS-01..DS-08 | PASS |
| DT-02 | Compression Floor — min CR ≥ 6.15× across DS-01..DS-10 | PASS |
| DT-03 | Determinism — 10,000 seeds bit-identical | PASS |
| DT-04 | Noise Robustness — NRMSE within limit under injected noise | PASS |
| DT-05 | Pathological Inputs — all-zeros, all-ones, NaN, Inf, step handled | PASS |
| DT-06 | RAM Budget — .data + .bss = 0 bytes | PASS |
| DT-07 | Latch Freedom — 10M samples encoded in 0.30 s | PASS |
| DT-09 | Latency — native 0.031 ms mean / 0.035 ms p99 | PASS |
| DT-11 | Cross-Platform Parity — 100 vectors bit-identical Ubuntu/macOS | PASS |
| DT-12 | Preset Coverage — 9 presets, all CR ≥ 6.24×, all NRMSE in bound | PASS |
| DT-14 | CRC Detection — 100% (150/150) | PASS |
| DT-16 | Benchmark Regression — degradation vs baseline within threshold | PASS |
| DT-17 | Provenance Integrity — DS-01..DS-10, DS-12 verified; DS-11 BLOCKED declared | PASS |
| DT-18 | Strict Gate Enforcement — mandatory SKIP rejected in strict mode | PASS |

Source: [`validation/results/dt_results_20260321T225304.json`](validation/results/dt_results_20260321T225304.json) + [`validation/results/release_preflight_report_20260321T205127.json`](validation/results/release_preflight_report_20260321T205127.json)

---

## Proof Anchors

| Path | State |
|------|-------|
| `proofs/artifacts/public_benchmarks/INDEX.json` | VERIFIED |
| `proofs/artifacts/public_benchmarks/DS-04.json` | VERIFIED |
| `proofs/artifacts/public_benchmarks/DS-07.json` | VERIFIED |
| `proofs/artifacts/public_benchmarks/DS-12.json` | VERIFIED |
| `validation/results/bench_summary_E1_real_public_20260321T225305.json` | VERIFIED |
| `validation/results/dt_results_20260321T225304.json` | VERIFIED |
| `validation/results/release_preflight_report_20260321T205127.json` | VERIFIED |
| `.github/workflows/ci.yml` | VERIFIED |

---

## Repo Shape

| Area | Purpose |
|---|---|
| `README.md`, `pyproject.toml`, `LICENSE` | repo front door and package metadata |
| `core/` | canonical Rust codec kernel and Rust test surface |
| `python/` | installable Python package and CLI |
| `docs/` | architecture, API, integration, and legal docs |
| `proofs/` | committed public benchmark receipts and related proof routing |
| `validation/` | datasets, destructive tests, benchmark scripts, and result artifacts |

---

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

---

## Upcoming Workstreams

This section captures the active lane priorities — what the next agent or contributor picks up, and what investors should expect. Cadence is continuous, not milestoned.

- **Production protocol bridge** — Active Engineering. Pick one of MQTT, Kafka, or SparkplugB; ship a thin adapter (encoder reads from broker → emits zpe-iot frames → decoder publishes back). Single SDK→deployment unlock.
- **DS-12 loss diagnosis** — Research-Deferred — Investigation Underway. Profile what about DS-12 made it lose; decide whether it is a bounded-corpus exclusion (announce) or a primitive gap (close).

---

### Latency and Throughput

Committed DT-09 result (per-window encode/decode, 256-sample window):

| Layer | Mean latency | p99 latency |
|---|---|---|
| Native (Rust) | 0.031 ms | 0.035 ms |
| Python (PyO3) | 0.723 ms | 0.789 ms |
| Threshold gate | mean < 0.500 ms | p99 < 2.000 ms |

Committed DT-07 result: 10 million samples encoded in 0.30 s (latch-freedom check, no queue buildup).

Sources: [`validation/results/dt_results_20260321T225304.json`](validation/results/dt_results_20260321T225304.json) (DT-07, DT-09) + CI job `strict_dt_smoke`

### Docs and Support

| Route | Target |
|---|---|
| Architecture | `docs/ARCHITECTURE.md` |
| API and CLI | `docs/API.md`, `docs/CLI_CONTRACT.md` |
| Benchmark authority | `proofs/artifacts/public_benchmarks/INDEX.json` |
| Legal boundary | `docs/LEGAL_BOUNDARIES.md` |
| Integration guidance | `docs/INTEGRATION_GUIDE.md` |
| Security reporting | `SECURITY.md` |

### Portfolio Position

ZPE-IoT is the constrained-telemetry lane in the [Zer0pa ZPE](https://github.com/Zer0pa) codec portfolio — one of 17 independent domain-specific encoding products, each with its own proof surface, sharing a license but not a shared platform.
