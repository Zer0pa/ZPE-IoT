# Research State

## Project Reference

See: `.gpd/PROJECT.md` (updated 2026-03-21)

**Machine-readable scoping contract:** `.gpd/state.json` field `project_contract`

**Core research question:** Can ZPE-IoT turn the bounded March 21, 2026 wedge into a cleaner technical closure by resolving preset parity, DS-05, native wheel packaging, expanded real-public benchmarking, and canonical observability without regressing the authority surface?
**Current focus:** Wave 2 technical closure on preset parity, DS-05, native wheel packaging, expanded real-public benchmarking, and canonical observability.

## Current Position

**Current Phase:** 08
**Current Phase Name:** Authority Surface Expansion
**Total Phases:** 10
**Current Plan:** 1
**Total Plans in Phase:** 1
**Status:** Executing
**Last Activity:** 2026-03-21
**Last Activity Description:** Closed Phase 7 with a cold-install native wheel proof, then opened Phase 8 authority-surface expansion.

**Progress:** [███████░░░] 70%

## Active Calculations

- Phase 7 is closed: the arm64 native-bundled wheel now proves `native_available = true` on cold install.
- Phase 8 is the live gate: expand the real-public authority surface from 8 to 12 datasets with reproducible provenance and a fresh widened benchmark rerun.
- The current authority baseline remains `validation/results/bench_summary_E1_real_public_20260321T182310.json` plus the fresh wheel proof in `proofs/artifacts/PHASE7_NATIVE_WHEEL_VERIFICATION_20260321.md`.

## Intermediate Results

- `[R-00-01-release-baseline]` Release authority baseline: March 20 managed preflight reports `17 PASS`, `0 FAIL`, `1 DEFERRED`, `0 critical failures`.
- `[R-00-02-dt-baseline]` Strict DT baseline: March 20 mandatory DT checks pass.
- `[R-00-03-bench-baseline]` Benchmark baseline: March 20 real public E1 reports `mean CR 4.369104600542837`, `wins 6/8`, current losses `DS-01` and `DS-05`.
- `[R-01-01-status-reconciliation]` Phase 1 produced `proofs/artifacts/STATUS_RECONCILIATION.md`, which freezes the March 20 authority surface and inventories the principal stale front-door contradictions.
- `[R-01-02-loss-diagnosis]` Phase 1 produced `validation/benchmarks/phase1_loss_scan.py`, `proofs/artifacts/LOSS_DIAGNOSIS_COMPACT.json`, and `proofs/artifacts/LOSS_DIAGNOSIS.md`.
- `[R-01-03-loss-verdict]` `DS-01` is not a simple threshold miss at near-current fidelity; `DS-05` is structurally weak under the current preset catalog relative to byte compressors.
- `[R-02-01-native-boundary]` `python/zpe_iot/_native.py` now mirrors Python WI-1 and ZH-1 wrappers, and wrapped-path parity tests pass.
- `[R-02-02-workstream-recheck]` Post-repair WI-1 and ZH-1 ablations still reject both candidates, but the only introduced strict failure is now `DT-10`.
- `[R-02-03-monotonicity-probe]` `proofs/artifacts/PHASE2_MONOTONICITY_PROBE_20260320.json` shows the threshold `0.1 -> 0.2` wrapped-size inversion survives zlib levels `1` through `9` for both workstreams.
- `[R-02-04-gap-budget]` Matching the current best baselines on `DS-01` and `DS-05` would lift the March 20 E1 mean only to about `4.7081x`, so Phase 2 must recover additional CR budget from already-winning datasets or a cross-dataset mechanism.
- `[R-02-05-byte-sink-slice]` `proofs/artifacts/PHASE2_BYTE_SINK_EXECUTION_SLICE_20260320.md` freezes the immediate blocker as missing byte-sink decomposition on the authority subset and converts it into four concrete execution tasks with a hard stop rule before any full E1 rerun.
- `[R-02-06-gap-budget]` `proofs/artifacts/PHASE2_GAP_BUDGET_20260321.json` proves the March 20 E1 artifact supports no single winning bridge dataset; after the generous `DS-01` plus `DS-05` ceiling, the smallest winning bridge set that can still clear the residual `2.3350685966624454` budget is `DS-02 + DS-06 + DS-08` if they each reach `5.0x`.
- `[R-02-07-overhead-decomposition]` `proofs/artifacts/PHASE2_OVERHEAD_DECOMPOSITION_20260321.json` shows that `DS-05`, `DS-02`, and `DS-08` share a smooth low-entropy payload sink family, while `DS-06` does not.
- `[R-02-08-candidate-shortlist]` `proofs/artifacts/PHASE2_CANDIDATE_SHORTLIST_20260321.md` converts the corrected blocker into three concrete solution tasks: smooth-series subset probe first, residual-budget recompute second, and DS-06-specific spend only if the subset still leaves a live path.
- `[R-02-09-smooth-series-tasking]` `proofs/artifacts/PHASE2_SMOOTH_SERIES_TASKING_20260321.md` freezes the current highest-leverage blocker as one admissible smooth-series subset probe, with explicit owner files, acceptance gates, and hard-stop rules before any wider rerun.
- `[R-02-10-smooth-series-probe]` `validation/benchmarks/phase2_smooth_series_probe.py` and `proofs/artifacts/PHASE2_SMOOTH_SERIES_PROBE_20260321.json` show the wrapper-neutral adaptive-threshold-gain candidate (`k=0.2`) improves compressed bytes on `DS-05`, `DS-02`, and `DS-08`, keeps subset `DT-10` monotonicity green, and lifts the projected E1 mean only to `4.4107x`, but it worsens benchmark `NRMSE(window-normalized)` on all three datasets, so the line hard-stops on fidelity before any `DS-06` spend or full E1 rerun.
- `[R-02-11-bitpack-feasibility]` `proofs/artifacts/PHASE2_TOKEN_BITPACK_FEASIBILITY_20260321.json` shows that the current balanced payload is dominated by `count == 1` token chunks across the decisive subset and across all E1 datasets, making one exact-fidelity count-aware bitpack attempt an evidence-backed next line rather than a speculative rewrite.
- `[R-02-12-bitpack-probe]` `proofs/artifacts/PHASE2_TOKEN_BITPACK_PROBE_20260321.json` shows the count-aware bitpack improves `DS-05`, `DS-02`, and `DS-08` with `NRMSE delta = 0.0`, keeps decode parity exact, and leaves both `DT-10` and `DT-11` green.
- `[R-02-13-bench-rerun]` `validation/results/bench_summary_E1_real_public_20260321T144350.json` lifts the real public E1 authority surface to `mean CR 6.557750648944099x` and `7/8`; `DS-05` remains the only competitor win.
- `[R-02-14-strict-dt-restored]` `validation/results/dt_results_20260321T144919.json` returns strict DT to `27 PASS`, `0 FAIL`, `0 SKIPPED`, `0 BLOCKED` after the raw E1 and Chemosense provenance inputs removed during disk cleanup were restored.
- `[R-03-01-blind-clone]` `proofs/artifacts/BLIND_CLONE_VERIFICATION.md` shows an equivalently clean `/tmp` workspace can reproduce the essential install and validation surface; the only exposed assumptions were an in-workspace native build for `DT-11` and a generated Chemosense summary artifact for `DT-25`.
- `[R-03-02-wheel]` `proofs/artifacts/WHEEL_VERIFICATION.md` shows `zpe_iot-0.1.0-py3-none-any.whl` builds cleanly and passes cold install/import/CLI smoke from `site-packages`, while keeping the pure-Python wheel boundary explicit via `native_available = false`.
- `[R-04-01-packet]` `proofs/team_assessment_packet_20260321/` now acts as the compact science and engineering assessment surface for this PRD.
- `[R-04-02-final-verdict]` `proofs/team_assessment_packet_20260321/05_FINAL_WEDGE_VERDICT.md` closes the PRD with explicit supported and unsupported claims.
- `[R-05-01-preset-canonicalization]` `.gpd/phases/05-preset-canonicalization/05-01-SUMMARY.md` and the updated Rust table show the Python values for `temperature`, `gps_track`, and `flow` are the only admissible canonical winners; the superseded Rust values achieved higher CR only by violating the current fidelity floor.
- `[R-06-01-ds05-closure]` `proofs/artifacts/PHASE6_DS05_STRUCTURAL_PROBE_20260321.json` shows the zero-special exact-fidelity packet route keeps fidelity and parity guardrails green, improves `DS-05` locally to `7.273695893451721x`, and justifies a fresh authority rerun.
- `[R-06-02-authority-rerun]` `validation/results/bench_summary_E1_real_public_20260321T182310.json` lifts the real public E1 surface to `mean CR 6.809761347280358x` and `8/8`, with `DS-05` no longer a competitor win.
- `[R-06-03-strict-dt]` `validation/results/dt_results_20260321T182603.json` keeps strict DT green at `27 PASS`, `0 FAIL`, `0 SKIPPED`, `0 BLOCKED` after the Phase 6 wire-format change.
- `[R-07-01-native-wheel]` `proofs/artifacts/PHASE7_NATIVE_WHEEL_VERIFICATION_20260321.md` shows `python -m build` produces a native-bundled arm64 wheel, a fresh install loads `zpe_iot._zpe_iot_native`, and `native_available = true` is real on cold install.

## Open Questions

- Can the wheel expose `native_available = true` on cold install while matching the ZPE-IMC packaging pattern exactly?
- Can the expanded 12-dataset real-public surface and canonical observability be added without reopening authority-surface regressions?
- Can the canonical Comet and Opik adapters be instantiated with live credentials, or will the lane stop at local-fallback evidence?

## Performance Metrics

| Label | Duration | Tasks | Files |
| ----- | -------- | ----- | ----- |
| Bootstrap | 2026-03-20 session | Contract persistence and project init | `.gpd/*` |
| Phase 1 | 2026-03-20 session | Research, plan, reconcile authority, build loss harness | `.gpd/phases/01-*`, `proofs/artifacts/STATUS_RECONCILIATION.md`, `validation/benchmarks/phase1_loss_scan.py`, `proofs/artifacts/LOSS_DIAGNOSIS*` |
| Phase 2 plan 02-01 | 2026-03-20 session | Repair native wrapper parity, rerun WI-1/ZH-1, and freeze the monotonicity verdict | `.gpd/phases/02-*`, `python/zpe_iot/_native.py`, `python/tests/test_*`, `validation/benchmarks/phase2_monotonicity_probe.py`, `proofs/artifacts/PHASE2_*` |
| Phase 2 plan 02-03 | 2026-03-21 session | Ratify and implement exact-fidelity token bitpacking, rerun E1, and restore strict-DT provenance floor | `.gpd/phases/02-*`, `python/zpe_iot/codec.py`, `core/src/bitpack.rs`, `validation/benchmarks/phase2_token_bitpack_*`, `proofs/artifacts/PHASE2_TOKEN_BITPACK_*`, `validation/results/bench_summary_E1_real_public_20260321T144350.json`, `validation/results/dt_results_20260321T144919.json` |
| Phase 3 | 2026-03-21 session | Verify clean-workspace reproduction and cold wheel smoke, then capture the honest portability boundaries | `.gpd/phases/03-*`, `proofs/artifacts/BLIND_CLONE_VERIFICATION.md`, `proofs/artifacts/WHEEL_VERIFICATION.md` |
| Phase 4 | 2026-03-21 session | Assemble the compact team packet and close the bounded wedge verdict | `.gpd/phases/04-*`, `proofs/team_assessment_packet_20260321/*` |
| Phase 5 | 2026-03-21 session | Ratify preset parity on `temperature`, `gps_track`, and `flow`, update the Rust canonical table, and rerun focused preset/parity verification | `.gpd/phases/05-*`, `core/src/presets.rs`, `python/tests/test_presets.py` |
| Phase 6 | 2026-03-21 session | Diagnose the remaining `DS-05` sink, implement an exact-fidelity zero-special packet route, rerun the authority benchmark, and keep strict DT green | `.gpd/phases/06-*`, `proofs/artifacts/PHASE6_DS05_STRUCTURAL_PROBE_20260321.json`, `validation/results/bench_summary_E1_real_public_20260321T182310.json`, `validation/results/dt_results_20260321T182603.json` |
| Phase 7 | 2026-03-21 session | Build the arm64 native wheel via maturin, prove cold-install `native_available = true`, and keep CLI smoke green | `.gpd/phases/07-*`, `proofs/artifacts/PHASE7_NATIVE_WHEEL_VERIFICATION_20260321.md`, `python/native/*`, `python/dist/zpe_iot-0.1.0-cp310-abi3-macosx_11_0_arm64.whl` |

## Accumulated Context

### Decisions

Full log: `.gpd/DECISIONS.md`

**Recent high-impact:**
- March 20 authority artifacts are sovereign; March 9 blocker narratives are not.
- Phase 1 is baseline reconciliation plus diagnostic harness, not premature uplift or status polishing.
- DS-01 does not justify threshold-tuning optimism inside the current fidelity regime.
- DS-05 is not meaningfully improved by the current preset catalog and likely requires algorithmic, not cosmetic, uplift work.
- The smooth-series tuning line is closed; the only remaining admissible Phase 2 spend was one exact-fidelity count-aware token-bitpack attempt.
- Raw E1 and Chemosense provenance artifacts are operationally required because strict DT depends on them; disk cleanup may remove only rebuildable outputs, not provenance floor inputs.
- Clean-room native build and Chemosense benchmark-summary generation are explicit portability steps, not hidden local assumptions.
- Cold wheel distribution is presently a pure-Python smoke claim, not bundled native parity.
- [Phase 0]: Start milestone v1.1 Wave 2 Technical Closure as a follow-on lane rather than pretending the closed v1.0 roadmap is still current. — The March 21, 2026 authority surface is green but preset parity, DS-05, native wheel packaging, observability, and benchmark breadth remain open engineering gaps.

### Active Approximations

| Approximation | Validity Range | Controlling Parameter | Current Value | Status |
| ------------- | -------------- | --------------------- | ------------- | ------ |
| Equivalently clean workspace may stand in for a duplicate blind clone only if disk pressure blocks a full clone and the substitution is explicitly documented | Disk-constrained local runs | Available free disk | Used and verified | Retired |
| Compact artifact retention favored over bulky duplicate logs, but not over provenance-floor inputs | Current local workstation | Disk headroom | Restored | Active |
| Phase 1 loss diagnosis is valid only for the unchanged real public E1 benchmark contract | Phase 1 diagnostic artifacts | Benchmark method lock | Active | Active |

**Convention Lock:**

- Authority baseline: March 20 managed preflight + strict DT + real public E1 benchmark
- Benchmark surface: unchanged real public E1
- Success gate: `mean CR >= 5.0x` and `PT-6 >= 7/8`, or an explicit evidence-backed failure verdict
- Date convention: absolute dates only for authority statements
- Proxy policy: auxiliary datasets and stale docs may inform diagnosis but may not substitute for the authority gate

### Propagated Uncertainties

| Quantity | Current Value | Uncertainty | Last Updated (Phase) | Method |
| -------- | ------------- | ----------- | -------------------- | ------ |
| `CR_mean` | `6.557750648944099x` | Current green authority value | Phase 2 | March 21 benchmark artifact |
| `PT6` | `7/8` | Current green authority value | Phase 2 | March 21 benchmark artifact |
| `DS-01` | `6.184694121802311x` vs `4.261137440758294x` best baseline | Closed on current authority surface | Phase 2 | March 21 benchmark artifact |
| `DS-05` | `6.631588755286225x` vs `7.021212770516391x` best baseline | Remaining authority-surface competitor win | Phase 2 | March 21 benchmark artifact |

### Pending Todos

- optional follow-on: design a bounded `DS-05` refinement lane without reopening the closed PRD gate
- optional follow-on: decide whether native-bundled wheel packaging is a worthwhile engineering investment
- preserve provenance-floor inputs during future cleanup while continuing to delete rebuildable outputs aggressively

### Blockers/Concerns

- `DS-05` remains the only competitor win on the green E1 surface, so the final wedge verdict must state that boundary explicitly rather than implying a clean sweep.
- The cold wheel currently demonstrates pure-Python smoke only; native-bundled distribution remains a follow-on choice, not a completed claim.
- The restored raw provenance artifacts now consume local disk again, so future cleanup must keep them intact while removing only rebuildable outputs.

## Session Continuity

**Last session:** 2026-03-21
**Stopped at:** `proofs/team_assessment_packet_20260321/05_FINAL_WEDGE_VERDICT.md` closes the PRD. The next action, if any, is refinement only: either widen the `DS-05` margin or decide whether wheel-native packaging should become a new scoped project.
**Resume file:** `.gpd/STATE.md`
