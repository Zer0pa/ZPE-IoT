# Roadmap: ZPE-IoT Authority Recovery And Wave 2 Technical Closure

## Overview

This roadmap starts from the real March 20, 2026 authority surface rather than the earlier blocked-state narrative. The work sequence is deliberate: freeze the authoritative baseline, diagnose the remaining benchmark losses, attempt honest uplift on the unchanged E1 surface, close portability evidence, and only then issue a bounded commercial verdict.

Milestone `v1.0` is closed. Milestone `v1.1` starts from the March 21, 2026 green authority surface and targets the remaining technical closure gaps without weakening the sovereign benchmark gate: preset parity, `DS-05`, native wheel packaging, real-public benchmark breadth, canonical observability, and a final gated accuracy pass.

## Contract Overview

| Contract Item | Advanced By Phase(s) | Status |
| ------------- | -------------------- | ------ |
| `claim-release-completion` | Phase 1, Phase 3, Phase 4 | Closed with March 20 preflight, March 21 strict DT, and final status packet |
| `claim-benchmark-wedge` | Phase 1, Phase 2, Phase 4 | Closed at `mean CR 6.557750648944099x` and `7/8`, with bounded DS-05 exception |
| `claim-honest-positioning` | Phase 1, Phase 3, Phase 4 | Closed with clean-workspace and cold-wheel evidence plus explicit claim limits |
| `deliv-loss-diagnosis` | Phase 1, Phase 2 | Phase 1 initial artifact complete |
| `deliv-blind-clone` | Phase 3 | Complete |
| `deliv-wheel-verification` | Phase 3 | Complete |
| `deliv-wedge-verdict` | Phase 4 | Complete |

## Phases

- [x] **Phase 1: Authority Baseline Reconciliation And Diagnostic Harness** - Reconcile the March 20 truth surface, freeze the live baseline, and build the DS-01 / DS-05 diagnostic harness.
- [x] **Phase 2: Targeted Compression Uplift** - Attempt honest E1 uplift on the unchanged benchmark surface, first by disproving the smooth-series tuning line and then by landing an exact-fidelity count-aware token bitpack that moves the authority metric cleanly.
- [x] **Phase 3: Portability, Blind-Clone, And Wheel Verification** - Close clean-environment and wheel-install evidence without relying on hidden local state.
- [x] **Phase 4: Honest Wedge Verdict And Engineering Completion** - Reconcile status docs and issue the bounded commercial verdict from the full authority surface.
- [ ] **Phase 5: Preset Canonicalization** - Canonicalize Rust and Python preset tables with explicit evidence for the remaining drifted presets and no DT/parity regression.
- [ ] **Phase 6: DS-05 Structural Closure** - Run one bounded follow-on mechanism against `DS-05`; either improve honestly or freeze the structural exception explicitly.
- [ ] **Phase 7: Native Wheel And Runtime Packaging** - Align ZPE-IoT packaging to the ZPE-IMC native-wheel pattern and verify cold native availability.
- [x] **Phase 8: Authority Surface Expansion** - Executed the widened authority-surface lane, producing an honest `11 READY + 1 BLOCKED` real-public manifest plus a rerun on the executable surface without pretending the exact 12-dataset target is closed.
- [x] **Phase 9: Benchmark Observability Integration** - Instantiated the canonical Classic Comet and Opik benchmark adapters, captured the explicit local-fallback evidence path, and removed the remaining drifted project-name usage.
- [ ] **Phase 10: Accuracy Pass And Final Gate** - Update only the designated inaccurate docs, rerun the full final gate, and write engineering-complete only if every gate is green.

## Phase Details

### Phase 1: Authority Baseline Reconciliation And Diagnostic Harness

**Goal:** Freeze the real March 20 authority baseline and build a compact diagnostic harness for the remaining E1 losses
**Depends on:** Nothing
**Requirements:** `ANAL-01`, `ANAL-02`, `BMK-01`, `VALD-01`
**Contract Coverage:**
- Advances: `claim-release-completion`, `claim-honest-positioning`, groundwork for `claim-benchmark-wedge`
- Deliverables: `deliv-status-docs`, `deliv-bench-summary`, `deliv-loss-diagnosis`
- Anchor coverage: `ref-preflight-20260320`, `ref-dt-20260320`, `ref-bench-e1-20260320`, `ref-public-audit`, `ref-wave2-brief`, `ref-team-status-summary`
- Forbidden proxies: `fp-stale-release-docs`, `fp-microfix-narrative`
**Success Criteria** (what must be TRUE):

1. March 20 preflight, DT, and E1 authority surfaces are mirrored in reconciled project docs with stale contradictions explicitly listed.
2. DS-01 and DS-05 each have a concrete diagnostic starting point, including dataset-level outcome capture and preset-drift inventory.
3. The project has a compact, unambiguous baseline from which uplift and portability work can proceed.
   **Plans:** 2 plans

Plans:

- [x] `01-01`: Reconcile March 20 authority artifacts against stale project docs and freeze the baseline.
- [x] `01-02`: Build the DS-01 / DS-05 diagnostic harness on the real public E1 surface.

### Phase 2: Targeted Compression Uplift

**Goal:** Determine whether the unchanged E1 surface can honestly support the target wedge threshold
**Depends on:** Phase 1
**Requirements:** `BMK-02`, `ANAL-02`
**Contract Coverage:**
- Advances: `claim-benchmark-wedge`
- Deliverables: `deliv-bench-summary`, `deliv-loss-diagnosis`, `deliv-wedge-verdict`
- Anchor coverage: `ref-bench-e1-20260320`, `ref-wave2-brief`, `ref-concerns-map`
- Forbidden proxies: `fp-chemosense-substitution`, `fp-cherrypicked-benchmark`
**Success Criteria** (what must be TRUE):

1. Targeted uplift experiments run on the unchanged real public E1 surface.
2. The project records whether `mean CR >= 5.0x` and `PT-6 >= 7/8` are met or not.
3. Any failure to reach the threshold is converted into evidence, not spin.
4. Phase 2 work does not pretend that `DS-01` plus `DS-05` closure alone is enough if the full E1 mean still stays below `5.0x`.
   **Plans:** 3 plans

Plans:

- [x] `02-01`: Design constrained uplift experiments against the current loss structure.
- [x] `02-02`: The smooth-series subset probe on `DS-05`, `DS-02`, and `DS-08` is now measured in `proofs/artifacts/PHASE2_SMOOTH_SERIES_PROBE_20260321.json`; it closes the parameter-tuning line because the candidate improves bytes but regresses benchmark fidelity.
- [x] `02-03`: `proofs/artifacts/PHASE2_TOKEN_BITPACK_FEASIBILITY_20260321.json` and `proofs/artifacts/PHASE2_TOKEN_BITPACK_PROBE_20260321.json` ratify and execute the exact-fidelity count-aware token-bitpack line, lifting the real public E1 authority surface to `mean CR 6.557750648944099x` and `7/8` with fresh strict DT green.

### Phase 3: Portability, Blind-Clone, And Wheel Verification

**Goal:** Close the portability and packaging evidence required for honest engineering-complete positioning
**Depends on:** Phase 1
**Requirements:** `VALD-02`, `VALD-03`
**Contract Coverage:**
- Advances: `claim-honest-positioning`
- Deliverables: `deliv-blind-clone`, `deliv-wheel-verification`
- Anchor coverage: `ref-preflight-20260320`, `ref-dt-20260320`, `ref-team-status-summary`
- Forbidden proxies: `fp-microfix-narrative`
**Success Criteria** (what must be TRUE):

1. A clean clone or equivalently clean workspace reproduces the essential install and validation surface, or the blocker is explicitly recorded.
2. A cold environment wheel build/install/import path is verified, or the blocker is explicitly recorded.
3. Portability claims are narrowed to the actual evidence rather than implied from the local dev environment.
   **Plans:** 2 plans

Plans:

- [x] `03-01`: `proofs/artifacts/BLIND_CLONE_VERIFICATION.md` closes the equivalently clean workspace path, including the explicit clean-room native-build and Chemosense-summary steps required for the decisive DT subset.
- [x] `03-02`: `proofs/artifacts/WHEEL_VERIFICATION.md` closes the cold wheel build/install/import smoke path from `site-packages`, with the pure-Python wheel boundary kept explicit.

### Phase 4: Honest Wedge Verdict And Engineering Completion

**Goal:** Convert the gathered evidence into reconciled status docs and a bounded commercial verdict
**Depends on:** Phases 1, 2, and 3
**Requirements:** `DOCS-01`
**Contract Coverage:**
- Advances: `claim-release-completion`, `claim-benchmark-wedge`, `claim-honest-positioning`
- Deliverables: `deliv-status-docs`, `deliv-wedge-verdict`
- Anchor coverage: all contract-critical references
- Forbidden proxies: all forbidden proxies remain active
**Success Criteria** (what must be TRUE):

1. Status docs accurately describe the March 20 authority surface and any remaining open blockers.
2. The wedge verdict states supported and unsupported claims explicitly.
3. No stale or proxy success narrative survives in the final project-facing artifact set.
   **Plans:** 2 plans

Plans:

- [x] `04-01`: `proofs/team_assessment_packet_20260321/` now acts as the compact science and engineering review packet.
- [x] `04-02`: `proofs/team_assessment_packet_20260321/05_FINAL_WEDGE_VERDICT.md` closes the PRD with explicit claim boundaries.

### Phase 5: Preset Canonicalization

**Goal:** Remove all remaining Rust/Python preset drift so cross-language encode and decode surfaces are truly canonical
**Depends on:** Phase 4
**Requirements:** `PAR-01`
**Success Criteria** (what must be TRUE):

1. `temperature`, `gps_track`, and `flow` have an explicit ratified value choice grounded in current data rather than taste.
2. Rust and Python preset tables agree for all 9 presets.
3. Focused parity and preset-floor checks pass after the change.
   **Plans:** 1 plan

Plans:

- [x] `05-01`: `.gpd/phases/05-preset-canonicalization/05-01-SUMMARY.md` ratifies the Python values for `temperature`, `gps_track`, and `flow` as the only admissible canonical winners because the prior Rust values violated the current fidelity floor; the Rust table, canonical tests, focused parity checks, and `DT-12` are now green.

### Phase 6: DS-05 Structural Closure

**Goal:** Determine whether the remaining `DS-05` loss can be improved honestly without reopening a regressing tuning loop
**Depends on:** Phase 5
**Requirements:** `BMK-03`
**Success Criteria** (what must be TRUE):

1. The phase executes one bounded mechanism family chosen from measured evidence, not a speculative parameter sweep.
2. `DS-05` either improves honestly or is explicitly frozen as a structural exception.
3. No wider authority-surface regression is smuggled in through the follow-on.
   **Plans:** 1 plan

Plans:

- [x] `06-01`: `proofs/artifacts/PHASE6_DS05_STRUCTURAL_PROBE_20260321.json` ratifies and verifies the zero-special exact-fidelity packet route; the fresh authority rerun in `validation/results/bench_summary_E1_real_public_20260321T182310.json` lifts the real public E1 surface to `mean CR 6.809761347280358x` and `8/8`.

### Phase 7: Native Wheel And Runtime Packaging

**Goal:** Move the wheel claim from pure-Python smoke to verified native-bundled distribution parity
**Depends on:** Phase 5
**Requirements:** `PKG-01`
**Success Criteria** (what must be TRUE):

1. ZPE-IoT follows the ZPE-IMC native-wheel pattern rather than inventing a new packaging convention.
2. Cold install proves `native_available = true`.
3. Pure-Python fallback remains intact when the native extension is absent.
   **Plans:** 1 plan

Plans:

- [x] `07-01`: `proofs/artifacts/PHASE7_NATIVE_WHEEL_VERIFICATION_20260321.md` closes the arm64 native wheel lane with a maturin-built wheel, cold-install `native_available = true`, and fresh-environment CLI smoke.

### Phase 8: Authority Surface Expansion

**Goal:** Make the benchmark surface harder to dismiss by adding four real-public datasets with provenance and rerun evidence
**Depends on:** Phase 6
**Requirements:** `DATA-01`
**Success Criteria** (what must be TRUE):

1. DS-09 through DS-12 are real-public, no-login, SHA256-captured inputs with manifest entries.
2. The expanded surface is rerun without cherry-picking or proxy substitution.
3. Any new structural losses are documented honestly rather than hidden.
   **Plans:** 1 plan

Plans:

- [x] `08-01`: `.gpd/phases/08-authority-surface-expansion/08-01-SUMMARY.md` records the widened `11 READY + 1 BLOCKED` surface, the `DS-11` no-login blocker, and the fresh rerun in `validation/results/bench_summary_E1_real_public_20260321T185546.json`.

### Phase 9: Benchmark Observability Integration

**Goal:** Restore canonical benchmark telemetry by instantiating Classic Comet and Opik exactly once and the same way every run
**Depends on:** Phase 7
**Requirements:** `OBS-01`
**Success Criteria** (what must be TRUE):

1. Classic Comet and Opik adapters use the canonical `zer0pa` workspace and the ratified project constants.
2. When credentials are present, the benchmark run logs live telemetry; when they are absent, the run stays local and says so explicitly.
3. The adapter surface does not mutate the authority artifacts or invent alternate project names.
   **Plans:** 1 plan

Plans:

- [x] `09-01`: `.gpd/phases/09-benchmark-observability-integration/09-01-SUMMARY.md` and `proofs/artifacts/PHASE9_BENCHMARK_OBSERVABILITY_20260321.md` close the canonical Comet/Opik adapter surface with explicit local-fallback evidence in `validation/results/benchmark_tracking_context_20260321T191046.json`.

### Phase 10: Accuracy Pass And Final Gate

**Goal:** Update only the factually wrong docs, rerun the full technical closure gate, and stop at green or honest failure
**Depends on:** Phases 6, 7, 8, and 9
**Requirements:** `DOCS-02`, `GATE-01`
**Success Criteria** (what must be TRUE):

1. Only the designated doc surfaces are changed, and each change matches current evidence.
2. The final gate sequence is rerun in one uninterrupted pass.
3. `proofs/ENGINEERING_COMPLETE_20260321.md` exists only if every gate is actually green.
   **Plans:** 1 plan

Plans:

- [ ] `10-01`: Run the narrow accuracy pass, execute the full final gate, and either write engineering-complete or record the honest failure surface.

## Progress

**Execution Order:**
Phases execute in numeric order: `1 -> 2 -> 3 -> 4`

| Phase | Plans Complete | Status | Completed |
| ----- | -------------- | ------ | --------- |
| 1. Authority Baseline Reconciliation And Diagnostic Harness | 2/2 | Complete | 2026-03-20 |
| 2. Targeted Compression Uplift | 3/3 | Complete | 2026-03-21 |
| 3. Portability, Blind-Clone, And Wheel Verification | 2/2 | Complete | 2026-03-21 |
| 4. Honest Wedge Verdict And Engineering Completion | 2/2 | Complete | 2026-03-21 |
| 5. Preset Canonicalization | 1/1 | Complete | 2026-03-21 |
| 6. DS-05 Structural Closure | 1/1 | Complete | 2026-03-21 |
| 7. Native Wheel And Runtime Packaging | 1/1 | Complete | 2026-03-21 |
| 8. Authority Surface Expansion | 1/1 | Complete | 2026-03-21 |
| 9. Benchmark Observability Integration | 1/1 | Complete | 2026-03-21 |
| 10. Accuracy Pass And Final Gate | 0/1 | Planned | - |
