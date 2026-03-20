# Research State

## Project Reference

See: `.gpd/PROJECT.md` (updated 2026-03-20)

**Machine-readable scoping contract:** `.gpd/state.json` field `project_contract`

**Core research question:** Can ZPE-IoT honestly claim a commercial wedge on the unchanged real public E1 surface while maintaining truthful release, portability, and packaging evidence?
**Current focus:** Phase 02: Targeted Compression Uplift

## Current Position

**Current Phase:** 02
**Current Phase Name:** Targeted Compression Uplift
**Total Phases:** 4
**Current Plan:** 0
**Total Plans in Phase:** 2
**Status:** Phase 1 complete; planning next
**Last Activity:** 2026-03-20
**Last Activity Description:** Completed Phase 1 research, planning, and execution by freezing the March 20 authority baseline and producing a compact DS-01 / DS-05 loss-diagnosis harness.

**Progress:** [██░░░░░░░░] 25%

## Active Calculations

- Planning targeted uplift work against the frozen Phase 1 baseline.
- Carrying forward only DT-safe uplift ideas onto the unchanged real public E1 surface.
- Preparing clean-environment closure work without inflating disk usage.

## Intermediate Results

- `[R-00-01-release-baseline]` Release authority baseline: March 20 managed preflight reports `17 PASS`, `0 FAIL`, `1 DEFERRED`, `0 critical failures`.
- `[R-00-02-dt-baseline]` Strict DT baseline: March 20 mandatory DT checks pass.
- `[R-00-03-bench-baseline]` Benchmark baseline: March 20 real public E1 reports `mean CR 4.369104600542837`, `wins 6/8`, current losses `DS-01` and `DS-05`.
- `[R-01-01-status-reconciliation]` Phase 1 produced `proofs/artifacts/STATUS_RECONCILIATION.md`, which freezes the March 20 authority surface and inventories the principal stale front-door contradictions.
- `[R-01-02-loss-diagnosis]` Phase 1 produced `validation/benchmarks/phase1_loss_scan.py`, `proofs/artifacts/LOSS_DIAGNOSIS_COMPACT.json`, and `proofs/artifacts/LOSS_DIAGNOSIS.md`.
- `[R-01-03-loss-verdict]` `DS-01` is not a simple threshold miss at near-current fidelity; `DS-05` is structurally weak under the current preset catalog relative to byte compressors.

## Open Questions

- Can a DT-safe uplift path move `mean CR` from `4.3691x` to `>= 5.0x` on the unchanged E1 surface?
- Can Phase 2 raise `PT-6` from `6/8` to `>= 7/8` without turning DS-01 or DS-05 into proxy wins?
- Is `WI-1` repairable under `DT-10` and `DT-11`, or does Phase 2 need a different algorithmic path?
- What is the smallest honest blind-clone and wheel-evidence package that closes engineering-complete positioning?

## Performance Metrics

| Label | Duration | Tasks | Files |
| ----- | -------- | ----- | ----- |
| Bootstrap | 2026-03-20 session | Contract persistence and project init | `.gpd/*` |
| Phase 1 | 2026-03-20 session | Research, plan, reconcile authority, build loss harness | `.gpd/phases/01-*`, `proofs/artifacts/STATUS_RECONCILIATION.md`, `validation/benchmarks/phase1_loss_scan.py`, `proofs/artifacts/LOSS_DIAGNOSIS*` |

## Accumulated Context

### Decisions

Full log: `.gpd/DECISIONS.md`

**Recent high-impact:**
- March 20 authority artifacts are sovereign; March 9 blocker narratives are not.
- Phase 1 is baseline reconciliation plus diagnostic harness, not premature uplift or status polishing.
- DS-01 does not justify threshold-tuning optimism inside the current fidelity regime.
- DS-05 is not meaningfully improved by the current preset catalog and likely requires algorithmic, not cosmetic, uplift work.

### Active Approximations

| Approximation | Validity Range | Controlling Parameter | Current Value | Status |
| ------------- | -------------- | --------------------- | ------------- | ------ |
| Equivalently clean workspace may stand in for a duplicate blind clone only if disk pressure blocks a full clone and the substitution is explicitly documented | Disk-constrained local runs | Available free disk | Tight | Conditional |
| Compact artifact retention favored over bulky duplicate logs | Current local workstation | Disk headroom | Tight | Active |
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
| `CR_mean` | `4.369104600542837x` | Authority value only; uplift unknown | Bootstrap | March 20 benchmark artifact |
| `PT6` | `6/8` | Improvement potential unknown | Bootstrap | March 20 benchmark artifact |
| `DS-01` | `3.9873890008950217x` vs `4.261137440758294x` best baseline | Algorithmic improvement path unknown | Phase 1 | Loss diagnosis compact scan |
| `DS-05` | `4.582866611384806x` vs `7.021212770516391x` best baseline | Current preset catalog ceiling likely below baseline | Phase 1 | Loss diagnosis compact scan |

### Pending Todos

None yet.

### Blockers/Concerns

- `DS-01` and `DS-05` remain open uplift problems, even though Phase 1 narrowed their likely failure modes.
- Blind-clone and wheel-install evidence are not yet closed in compact project artifacts.
- Disk headroom is tight enough that duplicate heavy artifacts can become a blocker by themselves.

## Session Continuity

**Last session:** 2026-03-20
**Stopped at:** Phase 1 complete; Phase 2 uplift planning is the next action.
**Resume file:** `.gpd/STATE.md`
