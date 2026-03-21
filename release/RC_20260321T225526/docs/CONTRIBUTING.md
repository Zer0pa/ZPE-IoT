# Contributing

## Development Setup

```bash
cd /path/to/zpe-iot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e './python[dev]'
```

## Required Local Checks

Run before opening a PR:

```bash
cargo test --manifest-path core/Cargo.toml --release
cargo clippy -- -D warnings

.venv/bin/python -m pytest -q
.venv/bin/python -m build ./python

.venv/bin/python validation/destruct_tests/run_all_dts.py --strict-gates
```

## Governance Rules

- Keep PRD/runbook history append-only.
- Do not weaken strict destructive gates.
- Do not run public publish steps without explicit ratification.
- Do not convert mixed evidence into a pass narrative.
- Keep performance work behind feature flags until strict gates prove no regressions.
