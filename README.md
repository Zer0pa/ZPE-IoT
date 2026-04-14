[![CI](https://github.com/Zer0pa/ZPE-IoT/actions/workflows/ci.yml/badge.svg)](https://github.com/Zer0pa/ZPE-IoT/actions/workflows/ci.yml)
<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# ZPE-IoT

[Docs](docs/README.md) | [Proofs](proofs/PROOF_INDEX.md) | [API](docs/API.md) | [Benchmarks](docs/BENCHMARKS.md) | [Release](docs/RELEASE_CHECKLIST.md) | [Audit](AUDITOR_PLAYBOOK.md)

SAL v6.2 — free below $100M annual revenue. See [LICENSE](LICENSE).

---

## What This Is

17× sensor compression without losing fidelity or determinism. 27/27 destructive tests passed. Bounded-lossy with byte-identical replay. Edge-deployable.

ZPE-IoT is a deterministic sensor compression SDK for constrained IoT streams — built for industrial IoT platform teams and edge telemetry vendors where transmission bandwidth is expensive, storage budgets are fixed, and lossy black-box codecs are unacceptable. Rust core, Python bindings via PyO3. Every metric traces to committed artifacts under `validation/` and `proofs/`.

The repo is **private-stage**. Install path and proof artifacts are real. Public package publication (PyPI / crates.io) deferred pending owner approval — acquisition today is repo checkout or owner-shared wheel.

**Not claimed:** public package availability, universal compressor dominance, lossless reconstruction, runtime coupling to ZPE-IMC, or multi-platform release.

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

| Field | Value |
|-------|-------|
| Architecture | SENSOR_STREAM |
| Encoding | DT_CODEC |

## Key Metrics

| Metric | Value | Baseline |
|--------|-------|----------|
| COMPRESSION | 17.16× | vs zstd 1.05–5.83× |
| E1_WINS | 10/11 | 11-dataset benchmark |
| DT_PASS | 27/27 | strict determinism |
| PREFLIGHT | 94.4% | managed preflight (17/18) |

> Source: [`proofs/FINAL_STATUS.md`](proofs/FINAL_STATUS.md), [`validation/results/bench_summary_E1_real_public_20260321T225305.json`](validation/results/bench_summary_E1_real_public_20260321T225305.json), [`validation/results/release_preflight_report_20260321T205127.json`](validation/results/release_preflight_report_20260321T205127.json), [`validation/results/dt_results_20260321T225304.json`](validation/results/dt_results_20260321T225304.json)

## Competitive Benchmarks

> Full competitive analysis: [`docs/BENCHMARKS.md`](docs/BENCHMARKS.md) | Source: [`proofs/artifacts/public_benchmarks/INDEX.json`](proofs/artifacts/public_benchmarks/INDEX.json)

| Tool | Compression Ratio | Notes |
|------|-------------------|-------|
| **ZPE-IoT** | **17.16× mean** | Active E1 surface, 10/11 wins |
| zstd (l3) | 1.05–5.83× on DS-01..DS-10 | ZPE-IoT wins 10/11; DS-12 loss at 5957.82× vs 120.47× |
| LZ4 | 1.00–2.91× on DS-01..DS-10 | ZPE-IoT wins 10/11; DS-12 loss at 234.06× vs 120.47× |
| zlib (l6) | 1.05–7.02× on DS-01..DS-10 | ZPE-IoT wins 10/11; DS-12 loss at 879.68× vs 120.47× |
| Gorilla-proxy | 1.04–6.22× on DS-01..DS-10 | ZPE-IoT wins 10/11; DS-12 loss at 814.11× vs 120.47× |

DS-12 is the explicit competitor-outlier slice on the active March authority surface. ZPE-IoT does not claim universal compressor dominance.

## What We Prove

> Auditable guarantees backed by committed proof artifacts. Start at `AUDITOR_PLAYBOOK.md`.

- 17.16× mean compression across 11 real public sensor datasets
- 27/27 destructive tests passed
- Byte-identical deterministic replay on tested corpus
- Managed preflight 17 PASS / 0 FAIL / 1 DEFERRED
- Fresh install smoke test PASS on arm64 macOS

## What We Don't Claim

- No claim of lossless reconstruction (bounded-lossy codec)
- No claim of PyPI publication readiness
- No claim of EnOcean or proprietary protocol support
- No claim of MQTT/LoRaWAN production bridge

<p>
  <img src=".github/assets/readme/section-bars/open-risks-non-blocking.svg" alt="OPEN RISKS (NON-BLOCKING)" width="100%">
</p>

### Open Risks (Non-Blocking)

| Risk lens | Current state |
|---|---|
| Publication | Public package publication remains deferred by policy; use the private repo or owner-shared wheel instead of claiming PyPI/crates.io availability. |
| Benchmark boundary | The active E1 surface is `DS-01..DS-10` plus `DS-12`; `DS-11` remains explicitly `BLOCKED`. |
| Comparator honesty | ZPE-IoT does not win every slice; `DS-12` is a competitor win on the current E1 real-public surface. |
| Native scope | Local arm64 macOS wheel install is verified; the multi-platform publish workflow exists but has not been executed as a public release event. |
| Fidelity boundary | ZPE-IoT is a bounded-lossy codec. It is not a fit for strict lossless reconstruction requirements. |

<p>
  <img src=".github/assets/readme/section-bars/quickstart-and-authority-point.svg" alt="QUICKSTART AND AUTHORITY POINT" width="100%">
</p>

## Commercial Readiness

| Field | Value |
|-------|-------|
| Verdict | STAGED |
| Commit SHA | b345798d3c7f |
| Confidence | 94.4% |
| Source | proofs/FINAL_STATUS.md |

> **Evaluators:** Ready for technical evaluation. `pip install -e .` in a clean venv. Contact hello@zer0pa.com for integration guidance.

### Authority Notes

| Field | Current truth | Evidence |
|---|---|---|
| As of | `2026-03-21` | [Final status](proofs/FINAL_STATUS.md) |
| Repository URL | `https://github.com/Zer0pa/ZPE-IoT` | [Citation](CITATION.cff) |
| Repo classification | `private-stage multi-surface codec repo` | [Technical alignment proof](proofs/artifacts/REPO_TECHNICAL_ALIGNMENT_20260321.md) |
| Release unit | `python/` distribution with bundled native wheel; `core/` and `c/` remain sibling engineering surfaces | [Technical alignment proof](proofs/artifacts/REPO_TECHNICAL_ALIGNMENT_20260321.md) |
| Acquisition surface | Private repo checkout or owner-shared built wheel from `python/dist/` | [Native wheel verification](proofs/artifacts/PHASE7_NATIVE_WHEEL_VERIFICATION_20260321.md) |
| Managed preflight | `17 PASS / 0 FAIL / 1 DEFERRED` | [Preflight report](validation/results/release_preflight_report_20260321T205127.json) |
| Strict DT | `27/27 PASS` | [DT report](validation/results/dt_results_20260321T225304.json) |
| Fresh install smoke | `PASS` on local arm64 macOS cold install | [Cold-install smoke](validation/results/fresh_env_smoke_20260321T205515/smoke.log) |
| Benchmark authority | `E1`, `10/11 wins`, `17.16x` mean CR | [E1 summary](validation/results/bench_summary_E1_real_public_20260321T225305.json) |
| Known real blockers | `none` | [Technical alignment proof](proofs/artifacts/REPO_TECHNICAL_ALIGNMENT_20260321.md) |
| Publication posture | `tag/index publication and outreach deferred pending explicit owner approval` | [Preflight report](validation/results/release_preflight_report_20260321T205127.json) |
| Canonical evidence entry | `proofs/PROOF_INDEX.md` | [Proof index](proofs/PROOF_INDEX.md) |

`Confidence` is derived from the managed-preflight completeness score in [`validation/results/release_preflight_report_20260321T205127.json`](validation/results/release_preflight_report_20260321T205127.json): `17 / 18 = 94.4%`.

## Tests and Verification

| Code | Check | Verdict |
|------|-------|---------|
| V_01 | Technical alignment | PASS |
| V_02 | Managed preflight | PASS |
| V_03 | Strict destructive tests | PASS |
| V_04 | E1 real-public benchmark | PASS |
| V_05 | Native wheel cold install | PASS |
| V_06 | Public package publication | INC |

`Managed preflight` is the build/install/release gate, `strict DT` is the destructive-test gate, and `E1` is the promoted real-public benchmark tier.

## Proof Anchors

| Path | State |
|------|-------|
| proofs/FINAL_STATUS.md | VERIFIED |
| proofs/artifacts/REPO_TECHNICAL_ALIGNMENT_20260321.md | VERIFIED |
| validation/results/release_preflight_report_20260321T205127.json | VERIFIED |
| validation/results/dt_results_20260321T225304.json | VERIFIED |
| validation/results/bench_summary_E1_real_public_20260321T225305.json | VERIFIED |
| validation/results/fresh_env_smoke_20260321T205515/smoke.log | VERIFIED |

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-2.gif" alt="ZPE-IoT Secondary Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/repo-shape.svg" alt="REPO SHAPE" width="100%">
</p>

## Repo Shape

| Field | Value |
|-------|-------|
| Proof Anchors | 6 |
| Modality Lanes | 9 |
| Authority Source | proofs/FINAL_STATUS.md |

`Modality Lanes` counts the nine preset lanes exposed by `python/zpe_iot/presets.py`.

### Directory Map

| Area | Purpose |
|---|---|
| `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`, `GOVERNANCE.md`, `RELEASING.md`, `ROADMAP.md`, `CITATION.cff`, `LICENSE` | Root truth, governance, release, and citation surface |
| `python/` | Installable Python distribution, CLI, and package metadata |
| `python/native/` | Repo-local PyO3 native build surface used for bundled wheels |
| `core/` | Canonical Rust codec kernel and test surface |
| `docs/` | Reader-facing architecture, benchmark, support, and legal routing |
| `docs/family/` | IMC contract-alignment artifacts; documentary only, not runtime-coupled |
| `proofs/` | Current verdict, proof routing, receipts, runbooks, and artifacts |
| `validation/` | Datasets, benchmarks, destructive tests, and generated result JSON |
| `project_docs/`, `release/RC_*` | Operator lineage and historical release packets, not the front-door authority surface |

## Quick Start

```bash
git clone https://github.com/Zer0pa/ZPE-IoT zpe-iot
cd zpe-iot
python -m pip install -e './python[dev]'
cargo test --manifest-path core/Cargo.toml --release
python validation/destruct_tests/run_all_dts.py --strict-gates
```

Acquisition surface: private repo checkout or owner-shared built wheel from `python/dist/`.

<p>
  <img src=".github/assets/readme/section-bars/contributing-security-support.svg" alt="CONTRIBUTING, SECURITY, SUPPORT" width="100%">
</p>

### Docs and Support

| Route | Target |
|---|---|
| Documentation index | `docs/README.md` |
| Canonical doc registry | `docs/DOC_REGISTRY.md` |
| Architecture and runtime map | `docs/ARCHITECTURE.md` |
| API and CLI details | `docs/API.md`, `docs/CLI_CONTRACT.md` |
| Benchmark authority and boundaries | `docs/BENCHMARKS.md` |
| Audit replay path | `AUDITOR_PLAYBOOK.md` |
| Public audit boundary | `PUBLIC_AUDIT_LIMITS.md` |
| Contribution rules | `CONTRIBUTING.md` |
| Support routing | `docs/FAQ.md` first, then `docs/SUPPORT.md`, then `SUPPORT.md` for repo-level policy |
| Security reporting | `SECURITY.md` |
| Legal/release boundary | `docs/LEGAL_BOUNDARIES.md`, `RELEASING.md` |

Treat `project_docs/` and older `release/RC_*` bundles as lineage. Current repo truth lives in the cited March 21 proof and validation artifacts above.

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>

## Ecosystem
This package is part of the [Zer0pa ZPE](https://github.com/Zer0pa) codec portfolio.
See also: zpe-xr, zpe-robotics, zpe-geo, zpe-finance, zpe-ink, zpe-multimodal, zpe-neuro, zpe-mocap, zpe-prosody, zpe-bio.

**Observability:** [Comet dashboard](https://www.comet.com/zer0pa/zpe-iot/view/new/panels) (public)

## Who This Is For

| | |
|---|---|
| **Ideal first buyer** | Industrial IoT platform team or edge telemetry vendor |
| **Pain** | High-frequency sensor streams overwhelm bandwidth and storage at the edge — generic compression breaks fidelity guarantees and replay determinism |
| **Deployment** | SDK with Rust core and Python bindings |
| **Family position** | Product candidate in the Zer0pa deterministic encoding family. ZPE-IMC is the umbrella integration layer |
