<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# Architecture

<p>
  <img src="../.github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

This document defines the current software architecture boundary for the ZPE-IoT always-in-beta repo.

Canonical anchors:

- Repository: `https://github.com/Zer0pa/ZPE-IoT`
- Repo license surface: `../LICENSE` (`LicenseRef-Zer0pa-SAL-6.2`); Rust crate manifests remain local MIT metadata for now
- Current proof router: `../validation/results/IOT_WAVE1_RELEASE_READINESS_REPORT.md` plus `../proofs/artifacts/public_benchmarks/INDEX.json`

<p>
  <img src="../.github/assets/readme/section-bars/repo-shape.svg" alt="REPO SHAPE" width="100%">
</p>

| Area | Role | Notes |
|---|---|---|
| `python/` | Installable Python distribution and CLI surface | Canonical release unit for local install and wheel build |
| `python/native/` | Repo-local PyO3 native build surface | Used by maturin to bundle the native extension |
| `core/` | Canonical Rust codec kernel | Holds the core encode/decode and validation logic |
| `c/` | Repo-local C surface | Example and local engineering surface, not a separate published package |
| `validation/` | Dataset, benchmark, and DT surface | Current authority metrics come from here |
| `proofs/` | Verdict, proof routing, and artifacts | Current status should route here, not to older release packets |

<p>
  <img src="../.github/assets/readme/section-bars/interface-contracts.svg" alt="INTERFACE CONTRACTS" width="100%">
</p>

| Stage | Encode responsibility | Decode responsibility | Canonical layer |
|---|---|---|---|
| Python package | Validate user input, resolve presets/config, and expose CLI/API entry points | Accept packet bytes or `EncodedStream` input for user-facing decode | Supporting wrapper |
| Native extension | Accelerate Python encode/decode when the bundled module is available | Mirror packet semantics under the Python runtime | Supporting wrapper |
| Rust core | Canonical packet construction, tokenization, bit-packing, CRC, and deterministic codec rules | Canonical packet parse and reconstruction rules | Canonical |
| Validation surface | Benchmark, DT, and install-path replay | Re-verify declared behavior against artifacts | Canonical for proof, not runtime |

<p>
  <img src="../.github/assets/readme/section-bars/public-api-contract.svg" alt="PUBLIC API CONTRACT" width="100%">
</p>

| Surface | Path | Truth |
|---|---|---|
| Python package | `python/zpe_iot/` | Primary user-facing package surface |
| Python CLI | `python/zpe_iot/cli.py` | Local CLI surface; contract details live in `CLI_CONTRACT.md` |
| Native extension | `python/native/` | Bundled into the local arm64 wheel proof path |
| Rust crate | `core/` | Canonical codec implementation and test surface |
| Family compatibility | `family/*` | Documentary/static alignment to IMC `wave1.0` only; no shared runtime substrate is claimed |

<p>
  <img src="../.github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

| Need | Artifact | Why it matters |
|---|---|---|
| Managed gate truth | `../validation/results/release_preflight_report_20260321T205127.json` | Current release-gate closure |
| Strict destructive testing | `../validation/results/dt_results_20260321T225304.json` | Governing validation surface |
| Benchmark authority | `../validation/results/bench_summary_E1_real_public_20260321T225305.json` | Promoted performance claim surface |
| Native install proof | `../validation/results/fresh_env_smoke_20260321T205515/smoke.log` | Cold-install evidence for the local arm64 wheel |
| Release manifest proof | `../validation/results/release_manifest_20260321T205457.json` | Current repo-local release manifest surface |

<p>
  <img src="../.github/assets/readme/section-bars/no-change-guarantees.svg" alt="NO CHANGE GUARANTEES" width="100%">
</p>

The following boundaries remain explicit:

- PyPI package publication is live; broader multi-platform release guarantees beyond the cited cold-install proof are not claimed here.
- ZPE-IoT aligns to ZPE-IMC by compatibility artifacts, not by runtime repo coupling.
- The active E1 benchmark surface excludes `DS-11`, which remains explicitly blocked.
- ZPE-IoT is a bounded-lossy codec and is not a strict lossless archive format.

<p>
  <img src="../.github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>
