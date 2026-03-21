# Final Wedge Verdict

Date: 2026-03-21

## Supported Claims

- On the promoted March 21 real-public E1 surface, ZPE-IoT clears the governing benchmark gate at `mean CR 17.163613932777356x` and `10/11` wins.
- Managed preflight and strict DT are substantively green, with only deferred publish work outside the current scope.
- Clean-workspace reproduction is verified.
- Native-bundled local arm64 macOS wheel build, install, import, and CLI smoke are verified.

## Unsupported Claims

- ZPE-IoT does not yet beat the best baseline on every dataset family.
- `DS-12` remains a competitor win on the promoted surface.
- Public publication is not yet complete.
- This PRD does not justify customer-validation or E2-market claims.

## Bounded Verdict

Within the scope of this PRD, ZPE-IoT now supports a truthful but bounded wedge claim.

Why that is justified:

- the authority benchmark moved on the unchanged E1 surface rather than on a proxy surface
- the move survived fresh strict DT
- the move also survived clean-workspace and cold-wheel verification

Why the verdict is bounded:

- `DS-12` remains a competitor win
- `DS-11` remains outside the promoted E1 surface
- the verified wheel claim is still local arm64 macOS, not a public multi-platform publication event

## Next Stage

Any further work should be refinement, not re-litigation of the now-closed PRD:

- attack `DS-05` if the team wants to widen the benchmark margin
- decide whether to widen the benchmark surface again once `DS-11` is either admitted or formally frozen
- pursue performance or implementation hardening only when it improves measured authority-relevant outcomes
