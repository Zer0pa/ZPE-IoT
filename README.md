<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# ZPE-IoT

[Docs](docs/README.md) | [Proofs](proofs/PROOF_INDEX.md) | [API](docs/API.md) | [Benchmarks](docs/BENCHMARKS.md) | [Release](docs/RELEASE_CHECKLIST.md) | [Audit](AUDITOR_PLAYBOOK.md)

---

## What This Is

ZPE-IoT is a deterministic sensor compression SDK for constrained IoT streams — time-series telemetry, chemosense packets, environmental sensor data. Rust core, Python bindings, edge-deployable.

The current evidence surface: **17.16× mean compression** across 11 real public sensor datasets, **27/27 destructive tests passed**, and deterministic byte-identical replay on the tested corpus. The codec is bounded-lossy — it trades a controlled fidelity budget for substantially smaller packets. Every claim traces to committed artifacts under `validation/` and `proofs/`.

This matters for teams running constrained sensor fleets where bandwidth is expensive, reproducibility is non-negotiable, and vendor-opaque compression is unacceptable. The SDK ships its own proof surface: benchmarks against real public data, destructive-test verdicts, and a documented fidelity envelope — not marketing numbers.

The repo is **private-stage**. The install path and proof artifacts are real. Public package publication (PyPI / crates.io) is deferred pending owner approval. Acquisition today is repo checkout or owner-shared wheel.

**Not claimed:** public package availability, universal compressor dominance, lossless reconstruction, runtime coupling to ZPE-IMC, or multi-platform release.

| Anchor | Artifact |
|---|---|
| Run-of-record benchmark | [`bench_summary_E1_real_public_20260321T225305.json`](validation/results/bench_summary_E1_real_public_20260321T225305.json) |
| Destructive-test verdicts | [`dt_results_20260321T225304.json`](validation/results/dt_results_20260321T225304.json) |
| Release preflight report | [`release_preflight_report_20260321T205127.json`](validation/results/release_preflight_report_20260321T205127.json) |

---

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

ZPE-IoT is a private-stage sensor compression SDK for 1D IoT time-series. The canonical implementation surface is the Rust core in `core/`, exposed through the nested Python distribution in `python/` and a repo-local PyO3 native build in `python/native/`.

This front door promotes only the March 21, 2026 repo-local authority surface. It does not claim public package availability, universal compressor dominance, or runtime coupling to ZPE-IMC.

<p>
  <img src=".github/assets/readme/section-bars/quickstart-and-authority-point.svg" alt="QUICKSTART AND AUTHORITY POINT" width="100%">
</p>

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
