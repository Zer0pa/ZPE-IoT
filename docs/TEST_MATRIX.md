# Test Matrix

Date: 2026-03-09

## Scope

Release-grade quality matrix for Rust core, Python SDK/CLI, destruct tests, and benchmark label governance.

## Unit and Property Tests

| Layer | Test File | Focus | Gate |
|---|---|---|---|
| Rust core | `core/tests/test_codec.rs` | deterministic encoding, balanced round-trip quality | E3.2 |
| Rust core | `core/tests/test_parity.rs` | token stability snapshot | E3.2 |
| Rust core | `core/tests/test_invariance.rs` | empty-input rejection, output truncation safety, FAST-mode finite decode | E3.2 |
| Python SDK | `python/tests/test_codec.py` | determinism, round-trip finite outputs, fidelity/compression, WI/ZH wrappers | E3.1 |
| Python SDK | `python/tests/test_presets.py` | preset construction + round-trip | E3.1 |
| Python SDK | `python/tests/test_native.py` | native availability/error paths | E3.1 |
| Python SDK | `python/tests/test_cli.py` | CLI e2e (csv->packet->csv), `--json`, diagnostics, exit-code behavior | E3.3 + E6 |
| Benchmark rules | `python/tests/test_benchmark_labels.py` | PT-6 label contract (`NOT_AVAILABLE`/`PROVISIONAL`/`FINAL`) | E3.4 |
| Benchmark rules | `python/tests/test_benchmark_label_golden.py` | golden-case regression for claim-tier labels | E3.4 |
| Fidelity semantics | `python/tests/test_fidelity_semantics.py` | named metric modes + label propagation | E2/E3 |
| DT regression | `python/tests/test_dt16_baseline_immutability.py` | DT-16 hash mismatch hard-fail | E3.3 |

## DT and Integration Gates

| Gate | Command | Expected |
|---|---|---|
| Strict DT mandatory set | `python validation/destruct_tests/run_all_dts.py --strict-gates` | mandatory PASS, no SKIPPED/BLOCKED |
| Baseline immutability | `DT-16` via strict runner | pinned baseline tag + manifest hash validation |
| Claim-tier compliance | `DT-19` via strict runner | evidence-tier labels enforced, zero-tier => `NOT_AVAILABLE` |
| Architecture tightness | `DT-21` via strict runner | no known circuitous benchmark/demo patterns |

## Coverage Threshold

- Enforced in `python/pyproject.toml` via pytest addopts:
  - `--cov=zpe_iot`
  - `--cov-fail-under=85`
- Latest March 9 artifact paths:
  - `validation/results/coverage/python_coverage.xml`
  - `validation/results/coverage/python_html/index.html`
- Latest observed result:
  - `70 passed`
  - `86.53%` total coverage

## Baseline Commands

```bash
cargo test --manifest-path core/Cargo.toml --release
cargo clippy -- -D warnings

.venv/bin/python -m pytest -q
.venv/bin/python validation/destruct_tests/run_all_dts.py --strict-gates
```

## Current Gap Note

The test matrix is not itself a release verdict.

As of 2026-03-09:

- core test surfaces are green
- Python and DT surfaces are green
- full release preflight is still blocked by `C07_SBOM_RELEASE_MANIFEST` and `C10_CHEMOSENSE_CLI_SMOKE`
