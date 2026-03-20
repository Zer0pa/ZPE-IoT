# Research State

## Project Reference

See: `.gpd/PROJECT.md` (updated 2026-03-20)

**Machine-readable scoping contract:** `.gpd/state.json` field `project_contract`

**Core research question:** Can ZPE-IoT honestly claim a commercial wedge on the unchanged real public E1 surface while maintaining truthful release, portability, and packaging evidence?
**Current focus:** Phase 01: Authority Baseline Reconciliation And Diagnostic Harness

## Current Position

**Current Phase:** 01
**Current Phase Name:** Authority Baseline Reconciliation And Diagnostic Harness
**Total Phases:** 4
**Current Plan:** 1
**Total Plans in Phase:** 2
**Status:** Researching
**Last Activity:** 2026-03-20
**Last Activity Description:** Approved scope, persisted the canonical project contract into `state.json`, and initialized minimal GPD project artifacts around the March 20 authority surface.

**Progress:** [░░░░░░░░░░] 0%

## Active Calculations

- Reconciling March 20 managed preflight, strict DT, and current public/status docs into a single truthful baseline.
- Building a compact DS-01 / DS-05 diagnostic harness on the unchanged real public E1 surface.
- Preparing clean-environment closure work without inflating disk usage.

## Intermediate Results

- `[R-00-01-release-baseline]` Release authority baseline: March 20 managed preflight reports `17 PASS`, `0 FAIL`, `1 DEFERRED`, `0 critical failures`.
- `[R-00-02-dt-baseline]` Strict DT baseline: March 20 mandatory DT checks pass.
- `[R-00-03-bench-baseline]` Benchmark baseline: March 20 real public E1 reports `mean CR 4.369104600542837`, `wins 6/8`, current losses `DS-01` and `DS-05`.

## Open Questions

- What exact stale-doc surfaces still contradict the March 20 release authority baseline?
- Is `DS-01` loss caused by preset drift, structural mismatch, or another factor?
- Is `DS-05` an intrinsic weakness for the current method or still tuneable?
- What is the smallest honest blind-clone and wheel-evidence package that closes engineering-complete positioning?

## Performance Metrics

| Label | Duration | Tasks | Files |
| ----- | -------- | ----- | ----- |
| Bootstrap | 2026-03-20 session | Contract persistence and project init | `.gpd/*` |

## Accumulated Context

### Decisions

Full log: `.gpd/DECISIONS.md`

**Recent high-impact:**
- March 20 authority artifacts are sovereign; March 9 blocker narratives are not.
- Phase 1 is baseline reconciliation plus diagnostic harness, not premature uplift or status polishing.

### Active Approximations

| Approximation | Validity Range | Controlling Parameter | Current Value | Status |
| ------------- | -------------- | --------------------- | ------------- | ------ |
| Equivalently clean workspace may stand in for a duplicate blind clone only if disk pressure blocks a full clone and the substitution is explicitly documented | Disk-constrained local runs | Available free disk | Tight | Conditional |
| Compact artifact retention favored over bulky duplicate logs | Current local workstation | Disk headroom | Tight | Active |

**Convention Lock:**

- Authority baseline: March 20 managed preflight + strict DT + real public E1 benchmark
- Benchmark surface: unchanged real public E1
- Success gate: `mean CR >= 5.0x` and `PT-6 >= 7/8`, or an explicit evidence-backed failure verdict
- Date convention: absolute dates only for authority statements
- Proxy policy: auxiliary datasets and stale docs may inform diagnosis but may not substitute for the authority gate

### Propagated Uncertainties

| Quantity | Current Value | Uncertainty | Last Updated (Phase) | Method |
| -------- | ------------- | ----------- | -------------------- | ------ |
| `CR_mean` | `4.369104600542837x` | Authority value only; uplift unknown | Bootstrap | March 20 benchmark artifact |
| `PT6` | `6/8` | Improvement potential unknown | Bootstrap | March 20 benchmark artifact |

### Pending Todos

None yet.

### Blockers/Concerns

- `DS-01` and `DS-05` are still structurally unresolved.
- Blind-clone and wheel-install evidence are not yet closed in compact project artifacts.
- Disk headroom is tight enough that duplicate heavy artifacts can become a blocker by themselves.

## Session Continuity

**Last session:** 2026-03-20
**Stopped at:** Minimal project bootstrap complete; Phase 1 research/planning/execution next.
**Resume file:** `.gpd/STATE.md`
