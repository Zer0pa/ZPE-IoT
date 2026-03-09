# Contributing

## Development Setup

```bash
cd '/Users/prinivenpillay/ZPE IoT/zpe-iot'
python3 -m venv .venv
source .venv/bin/activate
pip install -e ./python[dev]
```

## Required Local Checks

Run before opening a PR:

```bash
cd '/Users/prinivenpillay/ZPE IoT/zpe-iot/core'
cargo test
cargo clippy -- -D warnings

cd '/Users/prinivenpillay/ZPE IoT/zpe-iot/python'
../.venv/bin/python -m pytest -q
../.venv/bin/python -m build

cd '/Users/prinivenpillay/ZPE IoT/zpe-iot'
.venv/bin/python validation/destruct_tests/run_all_dts.py --strict-gates
.venv/bin/python validation/benchmarks/run_benchmarks.py
.venv/bin/python validation/benchmarks/generate_report.py
```

## Governance Rules

- Keep PRD/runbook history append-only.
- Do not weaken strict destructive gates.
- Do not run public publish steps without explicit ratification.
- Keep performance work behind feature flags until strict gates prove no regressions.
