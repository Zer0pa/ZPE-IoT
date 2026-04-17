<p>
  <img src="../../.github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# IoT Release Note for Wave-1 Coordination

Release Wave: `Wave-1`
IoT Package: `zpe-iot==0.1.0`
Status Date: `2026-03-21`

<p>
  <img src="../../.github/assets/readme/section-bars/release-notes.svg" alt="RELEASE NOTES" width="100%">
</p>

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

<p>
  <img src="../../.github/assets/readme/section-bars/downstream-action-items.svg" alt="DOWNSTREAM ACTION ITEMS" width="100%">
</p>

## Downstream Expectations
1. Bio/IMC/IoT coordination should use `docs/family/IOT_COMPATIBILITY_VECTOR.json` for wave-1 compatibility posture.
2. Any packet-version or dispatch-semantics break must trigger wave-note and compatibility vector update.
3. For live beta coordination, treat IMC linkage as a compatibility contract, not as runtime repo coupling.

## Deferred Actions
1. Broader public distribution and outreach beyond the live PyPI package remain owner-controlled.
2. Wider release-ceremony interlocks remain deferred until owner-ratified public truth alignment is wanted.

<p>
  <img src="../../.github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>
