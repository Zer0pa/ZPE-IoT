# Requirements: ZPE-IoT Authority Recovery And Wave 2 Technical Closure

**Defined:** 2026-03-20
**Core Research Question:** Can ZPE-IoT turn the bounded March 21, 2026 wedge into a cleaner technical closure by resolving preset parity, `DS-05`, native wheel packaging, expanded real-public benchmarking, and canonical observability without regressing the authority surface?

## Primary Requirements

### Analysis

- [x] **ANAL-01**: Reconcile all live project status surfaces to the March 20, 2026 managed preflight and strict DT authority artifacts, with stale contradictions explicitly enumerated.
- [x] **ANAL-02**: Build a dataset-level loss diagnosis for `DS-01` and `DS-05`, including preset drift, structural hypotheses, and concrete evidence.

### Benchmarking

- [x] **BMK-01**: Reproduce and freeze the current real public E1 authority baseline, including `mean CR`, `wins/total`, and dataset-level outcomes.
- [x] **BMK-02**: Run targeted uplift work on the unchanged E1 surface and record whether `mean CR >= 5.0x` and `PT-6 >= 7/8` are achieved or explicitly not achieved.

### Validation

- [x] **VALD-01**: Verify that March 20 managed preflight and strict DT remain the active release authority baseline and that deferred publish is described accurately.
- [x] **VALD-02**: Verify blind-clone or equivalently clean-workspace reproduction of the essential install and validation surface, or capture the exact blocker honestly.
- [x] **VALD-03**: Verify cold wheel build/install/import behavior in a fresh environment, or capture the exact blocker honestly.

### Documentation

- [x] **DOCS-01**: Produce reconciled status docs and a final wedge verdict that make only claims supported by the live authority artifacts.

## Wave 2 Requirements

### Parity

- [x] **PAR-01**: Canonicalize all 9 preset tables across Rust and Python, with explicit evidence for `temperature`, `gps_track`, and `flow`, and no parity or DT regression.

### Benchmarking

- [x] **BMK-03**: Run one bounded `DS-05` structural closure lane that either beats or nearly matches the best competitor without regressing benchmark fidelity or the wider authority surface, or records a structural exception honestly.
- [ ] **DATA-01**: Expand the real-public E1 surface from 8 to 12 datasets with no-login provenance, SHA256 capture, manifest entries, and a fresh benchmark rerun.

### Packaging

- [x] **PKG-01**: Build and verify a native-bundled wheel path aligned to the ZPE-IMC packaging pattern, with cold-install `native_available = true` evidence.

### Observability

- [ ] **OBS-01**: Instantiate Classic Comet and Opik benchmark adapters using the canonical `zer0pa` workspace and ratified project constants, with local fallback when credentials are absent.

### Documentation

- [ ] **DOCS-02**: Perform the tightly scoped March 21 truth-surface accuracy pass on the designated docs only.
- [ ] **GATE-01**: Rerun the full technical closure gate and write `proofs/ENGINEERING_COMPLETE_20260321.md` only if every declared gate is green.

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
| `PAR-01` | Rust and Python preset tables agree for all 9 presets with no DT-12 or parity regression | Compare preset tables, run focused preset evaluation, run parity tests |
| `BMK-03` | `DS-05` follow-on is either improved honestly or bounded honestly without wider regression | Measure candidate line on `DS-05` and rerun the authority surface only if guardrails hold |
| `DATA-01` | New datasets are real public, reproducible, and benchable | Verify provenance, manifest, preprocess path, and expanded benchmark rerun |
| `PKG-01` | Cold native wheel install proves bundled native availability | Build wheel via IMC-aligned Rust packaging surface and run fresh-environment smoke |
| `OBS-01` | Benchmark runs resolve the canonical Classic Comet and Opik projects or degrade cleanly to local evidence | Instantiate adapters, verify project checks, and capture run metadata |
| `DOCS-02` | Only factually wrong docs are updated and all updates match live evidence | Compare designated docs against latest authority artifacts |
| `GATE-01` | No engineering-complete artifact is written unless every final gate passes | Run the full final sequence and inspect the result set |

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
| `PAR-01` | Preset parity evidence, parity tests | March 21 codebase plus `DT-12` floor | Existing Rust/Python drift on `temperature`, `gps_track`, `flow` | Picking values by taste or cross-language inconsistency |
| `BMK-03` | `DS-05` probe artifact and, if admissible, fresh benchmark summary | March 21 green E1 surface | `DS-05` remains the only competitor win | Declaring a local byte win while fidelity or the wider surface regresses |
| `DATA-01` | Expanded manifest and benchmark summary | Real-public no-login sources | Existing E1 eight-dataset surface | Cherry-picking or unverifiable sources |
| `PKG-01` | Native wheel verification artifact | ZPE-IMC packaging pattern | Current cold wheel is pure Python only | Claiming native parity from an in-tree dev build |
| `OBS-01` | Benchmark telemetry adapter code and run artifact | Canonical project constants | Current repo has no Opik surface and stale `zpe-iot` Comet usage | Logging to ad hoc project names or hiding missing credentials |
| `DOCS-02` | Updated designated docs | March 21 authority artifacts and Wave 2 evidence | Current final packet and status docs | Prose cleanup that outruns the evidence |
| `GATE-01` | `proofs/ENGINEERING_COMPLETE_20260321.md` | Full final gate sequence | All prior follow-on evidence | Writing the completion marker before the real gate is green |

## Traceability

| Requirement | Phase | Status |
| ----------- | ----- | ------ |
| `ANAL-01` | Phase 1: Authority Baseline Reconciliation And Diagnostic Harness | Complete |
| `ANAL-02` | Phase 1: Authority Baseline Reconciliation And Diagnostic Harness | Complete |
| `BMK-01` | Phase 1: Authority Baseline Reconciliation And Diagnostic Harness | Complete |
| `BMK-02` | Phase 2: Targeted Compression Uplift | Complete |
| `VALD-01` | Phase 1: Authority Baseline Reconciliation And Diagnostic Harness | Complete |
| `VALD-02` | Phase 3: Portability, Blind-Clone, And Wheel Verification | Complete |
| `VALD-03` | Phase 3: Portability, Blind-Clone, And Wheel Verification | Complete |
| `DOCS-01` | Phase 4: Honest Wedge Verdict And Engineering Completion | Complete |
| `PAR-01` | Phase 5: Preset Canonicalization | Complete |
| `BMK-03` | Phase 6: DS-05 Structural Closure | Complete |
| `PKG-01` | Phase 7: Native Wheel And Runtime Packaging | Complete |
| `DATA-01` | Phase 8: Authority Surface Expansion | Planned |
| `OBS-01` | Phase 9: Benchmark Observability Integration | Planned |
| `DOCS-02` | Phase 10: Accuracy Pass And Final Gate | Planned |
| `GATE-01` | Phase 10: Accuracy Pass And Final Gate | Planned |

**Coverage:**

- Primary requirements: 8 total
- Wave 2 requirements: 7 total
- Mapped to phases: 15
- Unmapped: 0

---

_Requirements defined: 2026-03-20_
_Last updated: 2026-03-21 after starting milestone v1.1 Wave 2 Technical Closure_
