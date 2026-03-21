# Loss And Boundaries

Date: 2026-03-21

## What Phase 1 Established

The original blocking losses on March 20, 2026 were `DS-01` and `DS-05`.

- `DS-01` was not a simple threshold miss inside the near-authority fidelity regime
- `DS-05` was structurally weak under the then-current packetization relative to byte compressors

That diagnosis mattered because it prevented the project from wasting Phase 2 on preset storytelling.

## What Changed In Phase 2

Phase 2 did not tune around the loss surface. It changed the representation itself with exact-fidelity count-aware token bitpacking.

Result:

- `DS-01` is no longer a loss case on the authority benchmark
- `DS-05` improved materially from the earlier loss-phase result to `7.290115821056622x`
- `DS-05` is no longer a live loss case on the promoted authority benchmark; the active comparator loss is now `DS-12`

## Residual Boundary

The project now has the following bounded edges on the promoted authority surface:

- `DS-12` is a competitor win on the current promoted E1 surface
- `DS-11` remains blocked and is not part of the promoted surface
- multi-platform publication beyond the local arm64 macOS wheel is not yet claimed

This does not reopen the current PRD because the governing gate is already green. It does define the highest-value next-stage refinement lane if the team wants to deepen the advantage after closure.

## Non-Claims

The current evidence does not support saying:

- that ZPE-IoT dominates every dataset family
- that every blocked dataset is now admissible
- that the repo has already completed a public multi-platform release event

The correct position is green gate with bounded claim edges, not universal dominance.
