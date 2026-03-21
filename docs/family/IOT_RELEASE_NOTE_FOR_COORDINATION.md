# IoT Release Note for Wave-1 Coordination

Release Wave: `Wave-1`
IoT Package: `zpe-iot==0.1.0`
Status Date: `2026-03-21`

## Highlights
1. Release preflight is now checklist-driven with machine-readable gating report output.
2. Strict DT gate remains mandatory and non-weakened (`--strict-gates` policy retained).
3. Wire compatibility hardening added with golden fixtures and malformed/version assertions.
4. Managed preflight now closes at `17 PASS / 0 FAIL / 1 DEFERRED`, with only deferred publish left owner-controlled.
5. The active E1 benchmark surface closes at `10/11` wins across 11 READY real-public datasets.

## IMC Alignment
1. IMC contract consumed at `wave1.0`.
2. IMC vector SHA pinned to `9c8b905f6c1d30d057955aa9adf0f7ff9139853494dca673e5fbe69f24fba10e`.
3. Canonical cross-family demo authority remains IMC vector metric (`total_words=844`).

## Downstream Expectations
1. Bio/IMC/IoT coordination should use `docs/family/IOT_COMPATIBILITY_VECTOR.json` for wave-1 compatibility posture.
2. Any packet-version or dispatch-semantics break must trigger wave-note and compatibility vector update.
3. For private staging, treat IMC linkage as a compatibility contract, not as runtime repo coupling.

## Deferred Actions
1. External publishing remains deferred pending explicit ratification.
2. Public-release suite interlocks remain deferred until owner-ratified publication and final public truth alignment are complete.
