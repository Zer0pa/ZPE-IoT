<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# Fidelity Semantics Policy

Date: 2026-02-19  
Authority: PRD_06 Phase E2

<p>
  <img src="../.github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

## Objective

Prevent ambiguity between two valid NRMSE normalizations used in ZPE-IoT.

## Named Modes

- `NRMSE(dataset-normalized)`
  - Formula: `sqrt(MSE(window)) / (max(dataset) - min(dataset))`
  - Use when gate decisions must be comparable across windows of the same dataset.
  - Used by: `DT-01`, `DT-04`.

- `NRMSE(window-normalized)`
  - Formula: `sqrt(MSE(window)) / (max(window) - min(window))`
  - Use when comparing codec behavior per window in benchmark flows.
  - Used by: benchmark suite summaries and `DT-12`.

## Implementation Contract

- Shared source module: `validation/metrics/fidelity.py`.
- DT and benchmark code must import mode/label logic from this module.
- Benchmark artifacts must include:
  - `fidelity_metric_mode`
  - `fidelity_metric_label`
- Published benchmark tables must print explicit metric labels, never plain `NRMSE`.

## Prohibited Behavior

- Mixing dataset-normalized and window-normalized values in one table without labels.
- Reporting unlabeled `NRMSE` in customer-facing benchmark claims.

<p>
  <img src="../.github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>
