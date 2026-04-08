[![CI](https://github.com/Zer0pa/ZPE-IoT/actions/workflows/ci.yml/badge.svg)](https://github.com/Zer0pa/ZPE-IoT/actions/workflows/ci.yml)
<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# ZPE-IoT

[Docs](docs/README.md) | [Proofs](proofs/PROOF_INDEX.md) | [API](docs/API.md) | [Benchmarks](docs/BENCHMARKS.md) | [Release](docs/RELEASE_CHECKLIST.md) | [Audit](AUDITOR_PLAYBOOK.md)

SAL v6.0 — free below $100M annual revenue. See [LICENSE](LICENSE).

---

## What This Is

ZPE-IoT is a deterministic bounded-lossy sensor compression SDK for constrained IoT streams. It is not a strict lossless codec. Built for MQTT payloads, LoRaWAN uplinks, BLE sensor beacons, and other bandwidth-priced telemetry paths. Rust core. Python bindings via PyO3. Edge-deployable.

**17.16× mean compression** across 11 real public sensor datasets. **27/27 destructive tests passed.** Byte-identical deterministic replay on the tested corpus. Every metric traces to committed artifacts under `validation/` and `proofs/`.

Open-source IoT compression remains sparse. [`blisc`](https://github.com/marcauberer/blisc) is archived. Current verified install path: repo checkout plus editable build from `python/`.

| Baseline snapshot | Raw bytes | gzip bytes | ZPE bytes | Winner |
|---|---:|---:|---:|---|
| UCI AirQuality CO trace (`DS-01`, 8,960 samples) | 71,680 | 16,892 (`4.26x`) | 11,590 (`6.18x`) | zpe-iot |

Source: `validation/datasets/DS-01/data.npz`, evaluated locally with `zpe_iot.encode(..., preset="generic")` versus `gzip.compress(..., compresslevel=6)`.

| Anchor | Artifact |
|---|---|
| Run-of-record benchmark | [`bench_summary_E1_real_public_20260321T225305.json`](validation/results/bench_summary_E1_real_public_20260321T225305.json) |
| Destructive-test verdicts | [`dt_results_20260321T225304.json`](validation/results/dt_results_20260321T225304.json) |
| Release preflight report | [`release_preflight_report_20260321T205127.json`](validation/results/release_preflight_report_20260321T205127.json) |

---

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

ZPE-IoT is a sensor compression SDK for 1D IoT time-series. The canonical implementation surface is the Rust core in `core/`, exposed through the nested Python distribution in `python/` and a repo-local PyO3 native build in `python/native/`.

This front door promotes the March 21, 2026 repo-local authority surface. Repo checkout install is verified. Public package publication is not yet active.

<p>
  <img src=".github/assets/readme/section-bars/quickstart-and-authority-point.svg" alt="QUICKSTART AND AUTHORITY POINT" width="100%">
</p>

### Install

```bash
git clone https://github.com/Zer0pa/ZPE-IoT zpe-iot
cd zpe-iot
python -m pip install -e './python[dev]'
cargo test --manifest-path core/Cargo.toml --release
python validation/destruct_tests/run_all_dts.py --strict-gates
```

| Field | Current truth | Evidence |
|---|---|---|
| As of | `2026-03-21` | [Final status](proofs/FINAL_STATUS.md) |
| Repository URL | `https://github.com/Zer0pa/ZPE-IoT` | [Citation](CITATION.cff) |
| Repo classification | `multi-surface codec repo` | [Technical alignment proof](proofs/artifacts/REPO_TECHNICAL_ALIGNMENT_20260321.md) |
| Release unit | `python/` distribution with bundled native wheel; `core/` and `c/` remain sibling engineering surfaces | [Technical alignment proof](proofs/artifacts/REPO_TECHNICAL_ALIGNMENT_20260321.md) |
| Acquisition surface | Private repo checkout or owner-shared built wheel from `python/dist/` | [Native wheel verification](proofs/artifacts/PHASE7_NATIVE_WHEEL_VERIFICATION_20260321.md) |
| Managed preflight | `17 PASS / 0 FAIL / 1 DEFERRED` | [Preflight report](validation/results/release_preflight_report_20260321T205127.json) |
| Strict DT | `27/27 PASS` | [DT report](validation/results/dt_results_20260321T225304.json) |
| Fresh install smoke | `PASS` on local arm64 macOS cold install | [Cold-install smoke](validation/results/fresh_env_smoke_20260321T205515/smoke.log) |
| Benchmark authority | `E1`, `10/11 wins`, `17.16x` mean CR | [E1 summary](validation/results/bench_summary_E1_real_public_20260321T225305.json) |
| Known real blockers | `none` | [Technical alignment proof](proofs/artifacts/REPO_TECHNICAL_ALIGNMENT_20260321.md) |
| Publication posture | `tag/index publication and outreach deferred pending explicit owner approval` | [Preflight report](validation/results/release_preflight_report_20260321T205127.json) |
| Canonical evidence entry | `proofs/PROOF_INDEX.md` | [Proof index](proofs/PROOF_INDEX.md) |

`Managed preflight` is the build/install/release gate, `strict DT` is the destructive-test gate, and `E1` is the promoted real-public benchmark tier.

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-2.gif" alt="ZPE-IoT Secondary Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/repo-shape.svg" alt="REPO SHAPE" width="100%">
</p>

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

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/open-risks-non-blocking.svg" alt="OPEN RISKS (NON-BLOCKING)" width="100%">
</p>

| Risk lens | Current state |
|---|---|
| Publication | Public package publication remains deferred by policy; use the private repo or owner-shared wheel instead of claiming PyPI/crates.io availability. |
| Benchmark boundary | The active E1 surface is `DS-01..DS-10` plus `DS-12`; `DS-11` remains explicitly `BLOCKED`. |
| Comparator honesty | ZPE-IoT does not win every slice; `DS-12` is a competitor win on the current E1 real-public surface. |
| Native scope | Local arm64 macOS wheel install is verified; the multi-platform publish workflow exists but has not been executed as a public release event. |
| Fidelity boundary | ZPE-IoT is a bounded-lossy codec. It is not a fit for strict lossless reconstruction requirements. |

<p>
  <img src=".github/assets/readme/section-bars/contributing-security-support.svg" alt="CONTRIBUTING, SECURITY, SUPPORT" width="100%">
</p>

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

## ZPE Ecosystem
This package is part of the [Zer0pa ZPE](https://github.com/Zer0pa) codec portfolio.
See also: zpe-xr, zpe-robotics, zpe-geo, zpe-finance, zpe-ink, zpe-multimodal, zpe-neuro, zpe-mocap, zpe-prosody, zpe-bio.
