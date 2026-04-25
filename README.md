[![CI](https://github.com/Zer0pa/ZPE-IoT/actions/workflows/ci.yml/badge.svg)](https://github.com/Zer0pa/ZPE-IoT/actions/workflows/ci.yml)
<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# ZPE-IoT

[Architecture](docs/ARCHITECTURE.md) | [API](docs/API.md) | [Benchmarks](proofs/artifacts/public_benchmarks/INDEX.json) | [Package](python/README.md) | [Legal](docs/LEGAL_BOUNDARIES.md)

SAL v7.0 - free below $100M annual revenue. See [LICENSE](LICENSE).

---

## What This Is

ZPE-IoT is a deterministic sensor compression SDK for constrained telemetry streams. The repo ships a Rust core with PyO3 bindings, an installable Python package, committed benchmark receipts, and the validation scripts used to keep that surface honest.

This README is intentionally narrower than the March audit packet. Claims stay only where this repo currently has both committed proof artifacts and a CI check that exercises the relevant surface.

## CI-Backed Surface

The default CI workflow currently checks:

- Rust tests plus `cargo clippy -D warnings`
- editable install, wheel build, and Python test matrix on Ubuntu and macOS for CPython 3.10-3.12
- provenance smoke over the committed dataset manifest and transformed artifacts, plus DT-18 strict-gate enforcement
- public benchmark receipt sanity against the committed E1 benchmark summary and receipt index
- security scan plus release-manifest generation scripts

Source workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

## Public Benchmark Snapshot

The committed E1 public benchmark surface reports a 10/11 win split for ZPE-IoT across DS-01..DS-10 plus DS-12, with DS-12 remaining an explicit competitor win.

| Slice | Current committed receipt |
|------|----------------------------|
| E1 wins | 10 / 11 |
| DS-01..DS-10 mean compression | 6.65x |
| DS-01..DS-10 mean zstd compression | 2.87x |
| DS-12 | competitor win |
| DS-05 | ZPE-IoT win with a narrow margin over zlib |

Sources:

- [`validation/results/bench_summary_E1_real_public_20260321T225305.json`](validation/results/bench_summary_E1_real_public_20260321T225305.json)
- [`proofs/artifacts/public_benchmarks/INDEX.json`](proofs/artifacts/public_benchmarks/INDEX.json)
- [`proofs/artifacts/public_benchmarks/DS-05.json`](proofs/artifacts/public_benchmarks/DS-05.json)
- [`proofs/artifacts/public_benchmarks/DS-12.json`](proofs/artifacts/public_benchmarks/DS-12.json)

**Benchmark framing disclosure:** ZPE-IoT is a bounded-lossy codec. The published comparators in the E1 surface are lossless, so direct compression-ratio comparisons are informative but not apples-to-apples. DS-12 remains the explicit case where the comparator surface wins.

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

## Ecosystem

This package is part of the [Zer0pa ZPE](https://github.com/Zer0pa) codec portfolio.
