# Auditor Playbook

This is the shortest honest audit path for the staged ZPE-IoT repo.

It is not a public-release certification, not a publication claim, and not a substitute for Phase 5 verification.

## Start Here

1. Read `proofs/FINAL_STATUS.md`.
2. Read `PUBLIC_AUDIT_LIMITS.md`.
3. Inspect the latest managed preflight artifact:
   - `validation/results/release_preflight_report_20260309T040302.json`
4. Inspect the latest benchmark surface:
   - `docs/BENCHMARKS.md`
   - `validation/results/bench_summary_E1_real_public_20260309T060843.json`
5. Inspect the IMC compatibility surfaces:
   - `docs/family/IOT_COMPATIBILITY_VECTOR.json`
   - `docs/family/IOT_IMC_ALIGNMENT_REPORT.md`

## Shortest Local Verification Path

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e './python[dev]'
cargo test --manifest-path core/Cargo.toml --release
.venv/bin/python -m pytest -q
.venv/bin/python validation/destruct_tests/run_all_dts.py --strict-gates
```

## Current Truth On 2026-03-09

- Rust release tests: PASS
- Python pytest: PASS
- Strict DT: PASS
- Bench refresh: PASS
- Full release preflight: FAIL
  - `C07_SBOM_RELEASE_MANIFEST`
  - `C10_CHEMOSENSE_CLI_SMOKE`

## What This Repo Currently Proves

- the codebase is real and buildable
- the main Rust, Python, and strict DT surfaces currently pass locally
- the IMC wave1.0 pin is still intact
- the repo has evidence and release-bundle surfaces worth preserving

## What This Repo Does Not Yet Prove

- public package publication readiness
- blind-clone reproducibility
- clean release-manifest generation in the current managed environment
- final release readiness

If a replay disagrees, treat it as a mismatch against the staged evidence, not as a narrative dispute.
