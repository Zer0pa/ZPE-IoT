# Phase 2 Research

Date: 2026-03-21
Status: complete

## Question

After the smooth-series threshold line failed the benchmark-contract fidelity guardrail, is there still one evidence-backed Phase 2 method family worth executing before the wedge is downgraded?

## Inputs Read

- `validation/results/bench_summary_E1_real_public_20260320T174720.json`
- `proofs/artifacts/LOSS_DIAGNOSIS.md`
- `proofs/artifacts/PHASE2_GAP_BUDGET_20260321.json`
- `proofs/artifacts/PHASE2_OVERHEAD_DECOMPOSITION_20260321.json`
- `proofs/artifacts/PHASE2_SMOOTH_SERIES_PROBE_20260321.json`
- `python/zpe_iot/codec.py`
- `core/src/bitpack.rs`
- `validation/destruct_tests/dt10_monotonicity.py`
- `validation/destruct_tests/dt11_cross_platform.py`
- `proofs/artifacts/PHASE2_TOKEN_BITPACK_FEASIBILITY_20260321.json`

## Observed Signal

1. The first smooth-series payload-side mechanism is now closed as a bounded failure on the current line.
   `proofs/artifacts/PHASE2_SMOOTH_SERIES_PROBE_20260321.json` shows the `k=0.2` adaptive-threshold gain improved compressed bytes on `DS-05`, `DS-02`, and `DS-08`, but worsened benchmark `NRMSE(window-normalized)` on all three. Under the sovereign gate that is a hard stop, not a near miss.

2. The remaining byte sink is structural, not wrapper-level.
   `proofs/artifacts/PHASE2_OVERHEAD_DECOMPOSITION_20260321.json` already showed the relevant family is payload-dominated rather than header- or wrapper-dominated. Reading the actual balanced packet format confirms why: balanced and lossless streams currently spend 16 bits on every packed token chunk, including the overwhelmingly common `count == 1` case.

3. Count-aware bitpacking is the first live method family with exact-fidelity upside large enough to matter.
   `proofs/artifacts/PHASE2_TOKEN_BITPACK_FEASIBILITY_20260321.json` measures chunk-level token structure on `DS-01` through `DS-08` using the current quantiser and current tokens. The weakest `count == 1` share across the Phase 2 subset is still `0.8757567022196598`; the weakest share across the full E1 probe is `0.8410922463031062`. On the same 64-window probe surface, replacing the current 16-bit balanced chunks with a count-aware exact-fidelity bitstream projects:

- `DS-05`: `4.5753x -> 6.6265x`
- `DS-02`: `4.0464x -> 6.2332x`
- `DS-08`: `4.1416x -> 6.2894x`

When those subset estimates are stitched back onto the March 20 authority rows as a bounded projection, the probe reaches `projected mean CR 5.166123970558018x`. This is not yet authority closure, but it is large enough to justify one bounded implementation attempt before downgrading the wedge line.

## Candidate Families Considered

### 1. Another threshold or adaptive-parameter sweep

Reject. The measured scan already showed the cheap parameter families either fail to improve enough datasets or improve bytes by weakening benchmark fidelity. Spending more Phase 2 time there would violate the anti-proxy rule.

### 2. Wrapper retuning or experimental wrapper continuation

Reject. WI-1 and ZH-1 are no longer parity-blocked, but both remain `DT-10` failures and the monotonicity probe already ruled out simple wrapper-level retuning as the next honest spend.

### 3. Exact-fidelity count-aware token bitpack

Pursue. This family changes packet representation only. It does not change quantisation, thresholds, preset choice, or wrappers. In principle that means decode fidelity should remain identical, while the measured chunk statistics show enough structural slack to revive the benchmark line if the implementation survives `DT-10` and `DT-11`.

## Recommended Execution Slice

Implement one bounded prototype that:

1. adds a count-aware bitstream for balanced and lossless packets using the reserved packet flag bit, while preserving legacy decode compatibility
2. keeps fast mode and wrapper behavior unchanged
3. proves Python and Rust native packets stay bit-identical under the new format
4. reruns the decisive subset gate on `DS-05`, `DS-02`, and `DS-08`
5. reruns the full E1 authority benchmark only if the subset stays exact-fidelity and `DT-10` safe

## Hard Stops

- If decode fidelity changes at all on the subset, the line fails immediately.
- If Python and Rust packets diverge, the line fails immediately.
- If `DT-10` regresses, the line fails immediately.
- If the realized gain is materially below the feasibility ceiling and still leaves no credible route to `mean CR >= 5.0x`, Phase 2 should be downgraded honestly and portability work should move forward.

## Research Verdict

Phase 2 is not honestly closed yet. The smooth-series tuning line is closed, but there is still one evidence-backed structural line left: exact-fidelity count-aware token bitpacking. That is the only ratified next plan.
