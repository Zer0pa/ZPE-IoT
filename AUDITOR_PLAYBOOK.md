<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# Auditor Playbook

This is the shortest honest audit path for the current ZPE-IoT private-stage repo. It is not a public-release certification and not a claim of public package availability.

<p>
  <img src=".github/assets/readme/section-bars/quickstart-and-authority-point.svg" alt="QUICKSTART AND AUTHORITY POINT" width="100%">
</p>

1. Read `proofs/FINAL_STATUS.md`.
2. Read `PUBLIC_AUDIT_LIMITS.md`.
3. Inspect the current managed preflight artifact:
   - `validation/results/release_preflight_report_20260321T205127.json`
4. Inspect the current strict DT artifact:
   - `validation/results/dt_results_20260321T225304.json`
5. Inspect the current E1 benchmark surface:
   - `docs/BENCHMARKS.md`
   - `validation/results/bench_summary_E1_real_public_20260321T225305.json`
6. Inspect the runtime and install alignment proof:
   - `proofs/artifacts/REPO_TECHNICAL_ALIGNMENT_20260321.md`
   - `validation/results/fresh_env_smoke_20260321T205515/smoke.log`
7. Inspect the IMC compatibility surfaces:
   - `docs/family/IOT_COMPATIBILITY_VECTOR.json`
   - `docs/family/IOT_IMC_ALIGNMENT_REPORT.md`

<p>
  <img src=".github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e './python[dev]'
cargo test --manifest-path core/Cargo.toml --release
python -m pytest -q
python validation/destruct_tests/run_all_dts.py --strict-gates
bash scripts/release_preflight.sh
```

If you need to replay the native install path, build the wheel from `python/` and install the result from `python/dist/`.

<p>
  <img src=".github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

| Surface | Current truth |
|---|---|
| Managed preflight | `17 PASS / 0 FAIL / 1 DEFERRED` |
| Strict DT | `27/27 PASS` |
| Active E1 benchmark | `10/11` wins, `17.16x` mean CR |
| Local arm64 native wheel smoke | `PASS` |
| Publication | Deferred by policy |

<p>
  <img src=".github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

- the codebase is buildable and testable on the current private-stage surface
- the managed release gate passes aside from deferred publication
- the active real-public benchmark surface is reproducible and evidence-labeled
- the IMC `wave1.0` compatibility pin remains intact
- the repo can regenerate a current release bundle and supporting manifests

<p>
  <img src=".github/assets/readme/section-bars/out-of-scope.svg" alt="OUT OF SCOPE" width="100%">
</p>

- public PyPI or crates.io availability
- multi-platform wheel publication beyond the locally verified arm64 macOS path
- `DS-11` inclusion in the active E1 benchmark surface
- production behavior beyond the cited local artifacts

If a replay disagrees, treat it as a mismatch against the staged evidence, not as a narrative dispute.

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>
