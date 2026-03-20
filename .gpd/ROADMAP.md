# Roadmap: ZPE-IoT Authority Recovery And Wedge Validation

## Overview

This roadmap starts from the real March 20, 2026 authority surface rather than the earlier blocked-state narrative. The work sequence is deliberate: freeze the authoritative baseline, diagnose the remaining benchmark losses, attempt honest uplift on the unchanged E1 surface, close portability evidence, and only then issue a bounded commercial verdict.

## Contract Overview

| Contract Item | Advanced By Phase(s) | Status |
| ------------- | -------------------- | ------ |
| `claim-release-completion` | Phase 1, Phase 3, Phase 4 | Planned |
| `claim-benchmark-wedge` | Phase 1, Phase 2, Phase 4 | Planned |
| `claim-honest-positioning` | Phase 1, Phase 3, Phase 4 | Planned |
| `deliv-loss-diagnosis` | Phase 1, Phase 2 | Planned |
| `deliv-blind-clone` | Phase 3 | Planned |
| `deliv-wheel-verification` | Phase 3 | Planned |
| `deliv-wedge-verdict` | Phase 4 | Planned |

## Phases

- [ ] **Phase 1: Authority Baseline Reconciliation And Diagnostic Harness** - Reconcile the March 20 truth surface, freeze the live baseline, and build the DS-01 / DS-05 diagnostic harness.
- [ ] **Phase 2: Targeted Compression Uplift** - Attempt honest E1 uplift on the unchanged benchmark surface and decide whether the wedge threshold is realistically attainable.
- [ ] **Phase 3: Portability, Blind-Clone, And Wheel Verification** - Close clean-environment and wheel-install evidence without relying on hidden local state.
- [ ] **Phase 4: Honest Wedge Verdict And Engineering Completion** - Reconcile status docs and issue the bounded commercial verdict from the full authority surface.

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

- [ ] `01-01`: Reconcile March 20 authority artifacts against stale project docs and freeze the baseline.
- [ ] `01-02`: Build the DS-01 / DS-05 diagnostic harness on the real public E1 surface.

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
   **Plans:** 2 plans

Plans:

- [ ] `02-01`: Design constrained uplift experiments against the current loss structure.
- [ ] `02-02`: Execute uplift runs and compare them to the frozen E1 authority baseline.

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

- [ ] `03-01`: Run blind-clone or equivalently clean-workspace verification.
- [ ] `03-02`: Build the wheel and verify cold install/import behavior.

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

- [ ] `04-01`: Reconcile status docs to the full live evidence surface.
- [ ] `04-02`: Write the final wedge verdict with explicit claim boundaries.

## Progress

**Execution Order:**
Phases execute in numeric order: `1 -> 2 -> 3 -> 4`

| Phase | Plans Complete | Status | Completed |
| ----- | -------------- | ------ | --------- |
| 1. Authority Baseline Reconciliation And Diagnostic Harness | 0/2 | Not started | - |
| 2. Targeted Compression Uplift | 0/2 | Not started | - |
| 3. Portability, Blind-Clone, And Wheel Verification | 0/2 | Not started | - |
| 4. Honest Wedge Verdict And Engineering Completion | 0/2 | Not started | - |
