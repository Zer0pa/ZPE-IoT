# Requirements: ZPE-IoT Authority Recovery And Wedge Validation

**Defined:** 2026-03-20
**Core Research Question:** Can ZPE-IoT honestly claim a commercial wedge on the unchanged real public E1 surface while maintaining truthful release, portability, and packaging evidence?

## Primary Requirements

### Analysis

- [ ] **ANAL-01**: Reconcile all live project status surfaces to the March 20, 2026 managed preflight and strict DT authority artifacts, with stale contradictions explicitly enumerated.
- [ ] **ANAL-02**: Build a dataset-level loss diagnosis for `DS-01` and `DS-05`, including preset drift, structural hypotheses, and concrete evidence.

### Benchmarking

- [ ] **BMK-01**: Reproduce and freeze the current real public E1 authority baseline, including `mean CR`, `wins/total`, and dataset-level outcomes.
- [ ] **BMK-02**: Run targeted uplift work on the unchanged E1 surface and record whether `mean CR >= 5.0x` and `PT-6 >= 7/8` are achieved or explicitly not achieved.

### Validation

- [ ] **VALD-01**: Verify that March 20 managed preflight and strict DT remain the active release authority baseline and that deferred publish is described accurately.
- [ ] **VALD-02**: Verify blind-clone or equivalently clean-workspace reproduction of the essential install and validation surface, or capture the exact blocker honestly.
- [ ] **VALD-03**: Verify cold wheel build/install/import behavior in a fresh environment, or capture the exact blocker honestly.

### Documentation

- [ ] **DOCS-01**: Produce reconciled status docs and a final wedge verdict that make only claims supported by the live authority artifacts.

## Follow-Up Requirements

### Market Validation

- **MKT-01**: Test customer-facing commercial value on new external telemetry beyond the public E1 surface.

### Auxiliary Datasets

- **AUX-01**: Evaluate Chemosense or other non-E1 datasets only after the authority E1 surface is honestly resolved.

## Out Of Scope

| Topic | Reason |
| ----- | ------ |
| Public package publication | Deferred publish steps are outside the current project scope. |
| Chemosense-as-authority | Auxiliary datasets cannot substitute for the governing E1 benchmark surface. |
| Customer validation claims | New external evidence is required and is not present in this project. |
| Paid infrastructure | Not allowed without explicit approval. |

## Accuracy And Validation Criteria

| Requirement | Accuracy Target | Validation Method |
| ----------- | --------------- | ----------------- |
| `ANAL-01` | No contradiction between reconciled docs and March 20 authority artifacts | Compare reconciled docs against preflight, DT, and stale-doc surfaces |
| `ANAL-02` | Each of `DS-01` and `DS-05` has explicit evidence-backed diagnosis | Inspect dataset outcomes, preset drift, and rerun evidence |
| `BMK-01` | Reproduce the current E1 baseline exactly enough to preserve the authority surface | Compare against `bench_summary_E1_real_public_20260320T174720.json` |
| `BMK-02` | Honest result on unchanged E1 surface, either threshold met or bounded failure recorded | Re-run benchmark and compare against wedge threshold |
| `VALD-02` | Essential install/validation path works without undocumented local dependencies | Clean clone or equivalently clean workspace reproduction |
| `VALD-03` | Wheel install/import smoke path works in a fresh environment | Cold environment wheel verification |
| `DOCS-01` | No unsupported claims in final status or wedge verdict | Human review against contract references and forbidden proxies |

## Contract Coverage

| Requirement | Decisive Output / Deliverable | Anchor / Benchmark / Reference | Prior Inputs / Baselines | False Progress To Reject |
| ----------- | ----------------------------- | ------------------------------ | ------------------------ | ------------------------ |
| `ANAL-01` | `deliv-status-docs` | `ref-preflight-20260320`, `ref-dt-20260320`, `ref-public-audit` | March 20 authority baseline | Repeating stale March 9 blocker narrative |
| `ANAL-02` | `deliv-loss-diagnosis` | `ref-bench-e1-20260320` | Current losses `DS-01`, `DS-05` | Hand-wavy “probably tuneable” explanation |
| `BMK-01` | `deliv-bench-summary` | `ref-bench-e1-20260320` | `mean CR 4.3691x`, `6/8` | Auxiliary dataset wins presented as substitute baseline |
| `BMK-02` | `deliv-bench-summary`, `deliv-wedge-verdict` | `ref-bench-e1-20260320`, `ref-concerns-map` | Frozen unchanged E1 surface | Cherry-picked benchmark surface or excluded losses |
| `VALD-01` | `deliv-status-docs` | `ref-preflight-20260320`, `ref-dt-20260320` | Managed preflight + strict DT pair | “Engineering complete” language without citing the live artifacts |
| `VALD-02` | `deliv-blind-clone` | `claim-honest-positioning` | Current local workspace | Assuming clean-clone success from local imports |
| `VALD-03` | `deliv-wheel-verification` | `claim-honest-positioning` | Build artifacts from current repo | Assuming wheel health from source-tree execution |
| `DOCS-01` | `deliv-wedge-verdict` | `ref-concerns-map`, `ref-team-status-summary` | Approved scoping contract | Micro-fix or doc-polish narrative as substitute for authority evidence |

## Traceability

| Requirement | Phase | Status |
| ----------- | ----- | ------ |
| `ANAL-01` | Phase 1: Authority Baseline Reconciliation And Diagnostic Harness | Pending |
| `ANAL-02` | Phase 1: Authority Baseline Reconciliation And Diagnostic Harness | Pending |
| `BMK-01` | Phase 1: Authority Baseline Reconciliation And Diagnostic Harness | Pending |
| `BMK-02` | Phase 2: Targeted Compression Uplift | Pending |
| `VALD-01` | Phase 1: Authority Baseline Reconciliation And Diagnostic Harness | Pending |
| `VALD-02` | Phase 3: Portability, Blind-Clone, And Wheel Verification | Pending |
| `VALD-03` | Phase 3: Portability, Blind-Clone, And Wheel Verification | Pending |
| `DOCS-01` | Phase 4: Honest Wedge Verdict And Engineering Completion | Pending |

**Coverage:**

- Primary requirements: 8 total
- Mapped to phases: 8
- Unmapped: 0

---

_Requirements defined: 2026-03-20_
_Last updated: 2026-03-20 after project bootstrap_
