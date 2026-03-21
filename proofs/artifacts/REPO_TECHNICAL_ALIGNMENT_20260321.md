# Repo Technical Alignment

Date: 2026-03-21
Repo: `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot`
Workspace: `/Users/Zer0pa/ZPE/ZPE IoT`

## Classification

`zpe-iot` is a private-stage multi-surface codec repo:
- nested Python distribution and CLI in `python/`
- sibling Rust core crate in `core/`
- non-published PyO3 bridge in `python/native/`
- repo-local C surface in `c/`

## Target Architecture Chosen

The aligned technical release unit is the nested Python package in `python/`, with a bundled native wheel on supported targets, plus truthful sibling engineering surfaces:
- `python/` is the installable distribution and CLI surface
- `python/native/` remains the repo-local PyO3 build surface used by maturin
- `core/` remains the Rust kernel and C-linkable library surface
- `c/` remains a repo-local consumer/example surface
- family linkage stays static/documentary only; no runtime dependency on `ZPE-IMC`

## Technical Changes Made

- Added shared runtime/tool discovery in `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/scripts/runtime_surface.py` so release scripts resolve the active interpreter, venv tools, and CLI from the actual execution environment instead of a stale repo-root `.venv` assumption.
- Rewired `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/scripts/release_preflight.py`, `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/scripts/release_preflight.sh`, `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/scripts/security_scan.py`, and `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/scripts/generate_release_artifacts.py` to use that shared discovery layer.
- Split Python optional dependencies into truthful surfaces in `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/python/pyproject.toml` and declared release-tooling dependencies used by the real preflight path (`pip-audit`, `cyclonedx-bom`, `build`, `maturin`, `twine`) instead of leaving them implicit.
- Added repository/homepage/documentation metadata to `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/core/Cargo.toml` and `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/python/native/Cargo.toml` to eliminate packaging warnings in the actual build path.
- Fixed the Rust lint blocker in `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/core/src/codec.rs` by replacing the manual byte-round-up with `div_ceil`.
- Updated `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/python/README.md` to state the truthful install/runtime behavior for editable installs and bundled native wheels.
- Simplified the security/provenance CI job in `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/.github/workflows/ci.yml` so the release-tooling dependencies come from the declared package extras rather than ad hoc workflow-only installs.
- Added bounded observability tests in `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/python/tests/test_tracking.py` so the declared `pytest` coverage gate passes honestly on the tracked release path.
- Aligned `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/destruct_tests/dt17_provenance_integrity.py` with the active strict surface by verifying all READY datasets and separately validating that explicitly BLOCKED datasets remain explicitly declared, instead of turning the declared `DS-11` boundary into a false strict-gate failure.

## Verification Performed

- Rust tests passed: `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/release_preflight_report_20260321T205127.json`
- Rust clippy passed with warnings denied: `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/release_preflight_report_20260321T205127.json`
- Python tests passed with coverage above gate (`86.37%`): `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/release_preflight_report_20260321T205127.json`
- Strict DT suite passed `27/27`: `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/dt_results_20260321T225304.json`
- Build/install/preflight surface passed `17 PASS / 0 FAIL / 1 DEFERRED`: `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/release_preflight_report_20260321T205127.json`
- Fresh install smoke passed from a built wheel: `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/fresh_env_smoke_20260321T205515/smoke.log`
- Native wheel artifacts were built successfully: `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/python/dist/zpe_iot-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`
- SBOM and release manifests regenerated successfully:
  - `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/sbom_20260321T205457.json`
  - `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/sbom_python_20260321T205457.json`
  - `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/sbom_rust_20260321T205457.json`
  - `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/license_manifest_20260321T205457.json`
  - `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/release_manifest_20260321T205457.json`
- Security scan passed with no high/critical findings: `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/vulnerability_scan_20260321T205452.json`
- Release bundle regenerated successfully: `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/release/RC_20260321T225526/bundle_manifest.json`
- Benchmark split regenerated successfully on the aligned runtime path:
  - `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/bench_summary_E0_proxy_20260321T225305.json`
  - `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/bench_summary_E1_real_public_20260321T225305.json`
  - `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/validation/results/bench_summary_E2_real_customer_20260321T225305.json`

## Remaining Real Blockers

- none

This repo is technically aligned for final release-surface documentation and finalization.
