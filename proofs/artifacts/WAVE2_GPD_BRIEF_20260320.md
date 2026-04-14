# ZPE-IoT Engineering Completion PRD

## Autonomous Execution Brief - Wave 2

**Issue date:** 2026-03-20
**Governing repo:** https://github.com/Zer0pa/ZPE-IMC
**Working repo:** `zpe-iot/`
**Working lane:** ZPE IoT

## Core Question

Can ZPE-IoT earn a commercially credible wedge by proving truthful, reproducible compression advantage on the right IoT telemetry classes, while also closing release, portability, and packaging gates tightly enough for staged distribution?

## Physics/Product Thesis

ZPE-IoT encodes sensor residual motion through an 8-primitive direction alphabet:

`{flat, gentle+, moderate+, steep+, extreme+, extreme-, steep-, gentle-}`

The current stack is Rust core -> C ABI -> Python SDK -> CLI. The work is not to redesign the system from zero. The work is to determine, honestly and decisively:

1. where the geometric compression formalism structurally wins,
2. where it structurally loses,
3. whether those wins are strong enough to support a commercial wedge,
4. and whether the repo can be promoted from private staging candidate to reproducible distribution candidate.

## Current Truth Surface

Read in this order:

1. `<REPO_ROOT>/validation/results/release_preflight_report_20260320T154022.json`
2. `<REPO_ROOT>/validation/results/dt_results_20260320T174518.json`
3. `<REPO_ROOT>/proofs/FINAL_STATUS.md`
4. `<REPO_ROOT>/PUBLIC_AUDIT_LIMITS.md`
5. `<WORKSPACE>/ZPE IoT/team_status_packet_2026-03-20/00_STATUS_AND_AUGMENTATION_SUMMARY.md`
6. `<WORKSPACE>/ZPE IoT/.gpd/research-map/CONCERNS.md`

## Current Verified State As Of 2026-03-20

- Managed release preflight rerun on 2026-03-20 passed with `critical_failures=0`.
- Strict DT rerun on 2026-03-20 passed `27/27`.
- Historical repo truth docs are stale:
  - `proofs/FINAL_STATUS.md` still says `release readiness: BLOCKED` from 2026-03-09.
  - `PUBLIC_AUDIT_LIMITS.md` still points at the 2026-03-09 preflight as the latest gate truth.
- Benchmark surface is still below the original product target:
  - mean E1 compression ratio is `4.37x`
  - PT-6 is `6/8`
- Current machine constraints matter:
  - this workspace has about `4.5 GiB` free disk on 2026-03-20
  - large transient outputs must be pruned aggressively

## Governing Objective

We are not optimizing for a narratable win. We are optimizing for a truthful commercial wedge with materially better compression behavior than current market alternatives on the telemetry families where ZPE should win.

We are not committed to any specific story except one supported by authority evidence.

## Required Engineering Done Signal

Engineering is only closed when all of the following hold simultaneously:

1. managed preflight passes `18/18`,
2. strict DT passes `27/27`,
3. mean E1 CR is at least `5.0x`,
4. PT-6 is at least `7/8`,
5. cold-venv wheel install and smoke are green,
6. portability and blind-clone gaps are closed,
7. truth surfaces are reconciled so stale greener docs do not contradict current authority.

## Compute Envelope

### Local Mac

- Apple M1 Air
- release authority machine
- use for official managed preflight runs and packaging truth
- preferred Python range: `3.11` or `3.12`
- Rust target for managed gate work: `aarch64-apple-darwin`

### Red Magic 10 Pro+

- Android / Snapdragon 8 Elite
- use for ARM stress, Android cross-compile validation, and heavier field-style latency checks

### RunPod

- conditional only
- ask the user before using it
- use only when ablation compute exceeds local practicality

## Commercial Wedge Decision Rules

- If ZPE can be pushed to `>= 5.0x` mean E1 CR with `>= 7/8` PT-6 and no DT regressions, continue toward staged commercialization.
- If some datasets remain structural losses, describe them honestly and narrow the product wedge to structurally favorable telemetry rather than forcing a universal claim.
- If the structural ceiling remains too close to existing compressors, do not fake a wedge narrative.

## Must-Preserve Inputs

- Current passing managed preflight evidence from 2026-03-20
- Current benchmark truth showing `4.37x` mean E1 CR and `6/8` PT-6
- Prior research-map findings about stale docs, portability drift, and product-surface contradictions
- GitHub remote must remain `https://github.com/Zer0pa/ZPE-IoT`
- Work runs must be logged to Comet under the `zer0pa/zpe-iot` project

## False Progress To Reject

- a local micro-fix that does not improve the authority metric,
- benchmark storytelling that hides DS-01 or DS-05 losses,
- chemosense wins presented as a substitute for IoT-core benchmark wins,
- stale doc language treated as truth after newer authority evidence contradicts it,
- large artifact generation without disk-aware cleanup.

## Initial Phase Sketch

1. Reconcile the authority baseline and freeze the real starting state.
2. Diagnose the DS-01 and DS-05 loss structure and preset divergence.
3. Design and run targeted uplift experiments under disk and hardware constraints.
4. Close portability, blind-clone, and wheel-verification gaps.
5. Recompute the commercial wedge verdict honestly.

## Rethink Triggers

- Mean E1 CR remains below `5.0x` after disciplined targeted uplift attempts.
- PT-6 cannot be raised to `>= 7/8` without violating fidelity or DT gates.
- Blind-clone or portability work reveals the release story is still machine-coupled.
- The strongest truthful product framing narrows below a commercially useful wedge.
