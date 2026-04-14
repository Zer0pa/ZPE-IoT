# ZPE-IoT Authority Recovery And Wave 2 Technical Closure

## What This Is

This project uses the GPD workflow to decide whether ZPE-IoT currently has a truthful commercial wedge on the real public E1 IoT benchmark surface while preserving honest release and packaging claims. The governing evidence now starts from the March 21, 2026 closure surface: the green E1 benchmark rerun, strict DT recovery, clean-workspace portability proof, cold-wheel smoke proof, and the bounded final wedge verdict.

The expected outputs are compact engineering evidence artifacts rather than a paper. Milestone `v1.0` closed the bounded wedge honestly. Milestone `v1.1` now pursues technical closure on the remaining live engineering gaps without weakening the sovereign benchmark gate.

## Current Milestone: v1.1 Wave 2 Technical Closure

**Goal:** Convert the bounded March 21, 2026 wedge into a cleaner technical closure surface by fixing preset parity, attacking `DS-05` honestly, bundling the native wheel path, expanding the real-public benchmark surface, wiring canonical Comet/Opik observability, and updating only factually wrong docs.

**Target results:**

- Rust and Python preset tables agree for all 9 presets, with parity and DT evidence.
- `DS-05` is either lifted honestly or closed as a documented structural boundary under a non-regressing benchmark guardrail.
- Native wheel packaging is verified against the ZPE-IMC packaging pattern with a cold-install `native_available = true` proof.
- The authority benchmark surface expands from 8 to 12 real-public datasets with provenance and rerun evidence.
- Benchmark observability uses the canonical `zer0pa` workspace plus the ratified Classic Comet and Opik project constants, with local fallback when credentials are absent.

## Core Research Question

Can ZPE-IoT turn the bounded March 21, 2026 wedge into a cleaner technical closure by resolving preset parity, `DS-05`, native wheel packaging, expanded real-public benchmarking, and canonical observability without regressing the authority surface?

## Scoping Contract Summary

### Contract Coverage

- `claim-release-completion`: Closed in `v1.0`; follow-on work must not reopen it with stale blocker narratives.
- `claim-benchmark-wedge`: Closed in bounded form in `v1.0`; follow-on work may only improve or narrow the remaining `DS-05` boundary without weakening the benchmark surface.
- `claim-honest-positioning`: Closed in bounded form in `v1.0`; follow-on work may strengthen native wheel and observability claims only with new evidence.

### User Guidance To Preserve

- **User-stated observables:** March 20 release authority status, E1 mean CR, PT-6 win count, DS-01 and DS-05 diagnosis, portability evidence.
- **User-stated deliverables:** Reconciled status docs, benchmark authority summary, loss diagnosis dossier, blind-clone note, wheel verification note, wedge verdict.
- **Must-have references / prior outputs:** `ref-preflight-20260320`, `ref-dt-20260320`, `ref-bench-e1-20260320`, `ref-wave2-brief`, `ref-public-audit`, `ref-concerns-map`, `ref-team-status-summary`.
- **Stop / rethink conditions:** Any result that weakens the authority metric, any doc rewrite that outruns evidence, or any bulky artifact generation that does not materially move DS-01, DS-05, or reproducibility closure.

### Scope Boundaries

**In scope**

- Reconcile all project truth surfaces to the March 20, 2026 authority artifacts.
- Diagnose DS-01 and DS-05 on the real public E1 surface.
- Attempt honest uplift toward `mean CR >= 5.0x` and `PT-6 >= 7/8`.
- Close blind-clone and wheel verification evidence.
- Produce a direct, bounded commercial wedge verdict.

**Out of scope**

- Public publication or marketplace release during this project.
- Treating Chemosense or any non-E1 dataset as substitute authority evidence.
- Customer validation claims without new external evidence.
- Paid infrastructure such as RunPod without explicit approval.

### Active Anchor Registry

- `ref-preflight-20260320`: `<REPO_ROOT>/validation/results/release_preflight_report_20260320T154022.json`
  - Why it matters: Defines the live release-preflight authority surface.
  - Carry forward: `planning`, `execution`, `verification`, `writing`
  - Required action: `read`, `compare`, `cite`
- `ref-dt-20260320`: `<REPO_ROOT>/validation/results/dt_results_20260320T174518.json`
  - Why it matters: Confirms strict DT closure on March 20, 2026.
  - Carry forward: `planning`, `execution`, `verification`, `writing`
  - Required action: `read`, `compare`, `cite`
- `ref-bench-e1-20260320`: `<REPO_ROOT>/validation/results/bench_summary_E1_real_public_20260320T174720.json`
  - Why it matters: Defines the current benchmark authority surface, including `mean CR 4.3691x`, `wins 6/8`, and the `DS-01` / `DS-05` losses.
  - Carry forward: `planning`, `execution`, `verification`, `writing`
  - Required action: `read`, `compare`, `cite`
- `ref-wave2-brief`: `<REPO_ROOT>/proofs/artifacts/WAVE2_GPD_BRIEF_20260320.md`
  - Why it matters: Preserves the user brief and the anti-proxy framing.
  - Carry forward: `planning`, `execution`
  - Required action: `read`, `use`
- `ref-public-audit`: `<REPO_ROOT>/PUBLIC_AUDIT_LIMITS.md`
  - Why it matters: Captures the stale blocked-state surface that must now be reconciled.
  - Carry forward: `planning`, `execution`, `verification`
  - Required action: `read`, `compare`, `avoid`
- `ref-concerns-map`: `<WORKSPACE>/ZPE IoT/.gpd/research-map/CONCERNS.md`
  - Why it matters: Preserves the outer commercial-wedge concerns and forbidden-proxy discipline.
  - Carry forward: `planning`, `execution`, `verification`, `writing`
  - Required action: `read`, `use`
- `ref-team-status-summary`: `<WORKSPACE>/ZPE IoT/team_status_packet_2026-03-20/00_STATUS_AND_AUGMENTATION_SUMMARY.md`
  - Why it matters: Supplies the current internal status framing and augmentation priorities.
  - Carry forward: `planning`, `execution`, `writing`
  - Required action: `read`, `use`

### Carry-Forward Inputs

- `<REPO_ROOT>/proofs/artifacts/WAVE2_GPD_BRIEF_20260320.md`
- `<WORKSPACE>/ZPE IoT/team_status_packet_2026-03-20/00_STATUS_AND_AUGMENTATION_SUMMARY.md`
- `<WORKSPACE>/ZPE IoT/team_status_packet_2026-03-20/04_BENCHMARKS.md`
- March 20 preflight, DT, and E1 authority artifacts

### Skeptical Review

- **Weakest anchor:** The exact structural causes of DS-01 and DS-05 are not yet pinned down.
- **Unvalidated assumptions:** A constrained preset or parameter change may still recover at least one remaining E1 loss without weakening the benchmark surface.
- **Competing explanation:** DS-05 may be intrinsically weak for the current compression strategy rather than just under-tuned.
- **Disconfirming observation:** If honest uplift attempts still leave the unchanged E1 surface below threshold, the project must conclude that the wedge is not yet established.
- **False progress to reject:** Stale docs, Chemosense substitution, cherry-picked benchmark subsets, and micro-fix narratives that do not move the authority gate.

### Open Contract Questions

- Can the unchanged E1 surface reach `mean CR >= 5.0x` without invalid benchmarking?
- Can PT-6 move from `6/8` to at least `7/8`?
- Is `DS-05` structural, tuneable, or still inconclusive?
- What exact portability and packaging evidence is still required beyond the current `17 PASS + 1 DEFERRED` release baseline?

## Research Questions

### Answered

- March 20, 2026 preflight and DT have superseded the earlier blocked-state release narrative.

### Active

- [ ] Which preset values for `temperature`, `gps_track`, and `flow` should be canonical across Rust and Python under the current DT-12 and parity gates?
- [ ] Can `DS-05` be lifted to competitor parity or victory without regressing benchmark fidelity or the wider authority surface?
- [ ] Can the wheel expose `native_available = true` on cold install while following the ZPE-IMC packaging pattern exactly?
- [ ] Can the real-public benchmark surface expand to 12 datasets with truthful provenance and still support the existing wedge?
- [ ] Can Classic Comet and Opik logging be instantiated with the canonical project constants and degrade locally when credentials are absent?

### Out Of Scope

- External customer validation without new field evidence.
- Public release publication during this project.

## Research Context

### Physical System

ZPE-IoT is an IoT telemetry compression system evaluated against the real public E1 benchmark surface and release-engineering gates such as preflight, DT, clean-environment install, and wheel importability.

### Theoretical Framework

This is an empirical benchmarking and release-authority project rather than a formal derivation project. The governing logic is benchmark integrity, reproducibility, and evidence discipline.

### Key Parameters And Scales

| Parameter | Symbol | Regime | Notes |
| --------- | ------ | ------ | ----- |
| Mean compression ratio | `CR_mean` | Current baseline `4.3691046005x` | Real public E1 authority metric |
| PT-6 win rate | `PT6` | Current baseline `6/8` | Current losses are `DS-01` and `DS-05` |
| Release authority | `RA` | `17 PASS + 1 DEFERRED`, `0 FAIL`, `0 critical` | March 20, 2026 managed preflight |
| Strict DT | `DT` | Mandatory checks pass | March 20, 2026 strict DT |
| Disk headroom | `disk_free` | Tight | About `4.5 GiB` at project start |

### Known Results

- March 20 managed preflight closed substantive release-preflight gates with only deferred publish remaining.
- March 21 strict DT returned to `27 PASS`, `0 FAIL`, `0 SKIPPED`, `0 BLOCKED`.
- March 21 real public E1 benchmark closed at `mean CR 6.557750648944099x` and `7/8`, with `DS-05` as the only remaining competitor win.
- Clean-workspace portability and cold-wheel smoke are closed at bounded scope, but native-bundled distribution parity is not yet established.

### What Is New

This follow-on milestone starts from the already-green March 21 authority surface and targets the remaining engineering gaps that still weaken the technical closure story: preset parity, `DS-05`, native wheel packaging, benchmark-surface breadth, and benchmark observability.

### Target Venue

Internal authority packet and commercial diligence artifacts for ZPE-IoT. If the evidence later supports it, these outputs can feed updated public status docs.

### Computational Environment

Primary execution environment is the local Mac M1 Air workspace at `<REPO_ROOT>`, with disk pressure treated as a real constraint. Clean-environment checks must stay compact and reproducible.

## Notation And Conventions

See `.gpd/CONVENTIONS.md` for project conventions and `.gpd/NOTATION_GLOSSARY.md` for shorthand labels.

## Unit System

Use literal engineering units and benchmark counts. Dates should be recorded as absolute calendar dates, not relative labels.

## Requirements

See `.gpd/REQUIREMENTS.md` for the checkable requirement set.

Key requirement categories: `ANAL`, `BMK`, `VALD`, `DOCS`

## Key References

- `ref-preflight-20260320`
- `ref-dt-20260320`
- `ref-bench-e1-20260320`
- `ref-wave2-brief`
- `ref-public-audit`
- `ref-concerns-map`
- `ref-team-status-summary`

## Constraints

- **Authority**: March 20, 2026 artifacts are sovereign unless superseded by newer reproducible evidence.
- **Benchmark integrity**: The unchanged real public E1 surface remains the governing benchmark gate.
- **Portability**: Clean-environment install evidence must be real, not implied from local state.
- **Disk**: Artifact generation must stay compact because local disk headroom is limited.
- **Git**: The existing dirty worktree is real; unrelated user changes must not be reverted.

## Key Decisions

| Decision | Rationale | Outcome |
| -------- | --------- | ------- |
| Treat March 20 authority artifacts as canonical | Older March 9 blocker docs are stale | Active |
| Start with reconciliation and diagnostic harness | Honest uplift work needs a frozen baseline first | Active |

Full log: `.gpd/DECISIONS.md`

---

_Last updated: 2026-03-21 after starting milestone v1.1 Wave 2 Technical Closure_
