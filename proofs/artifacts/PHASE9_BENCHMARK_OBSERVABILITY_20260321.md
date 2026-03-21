# Phase 9 Benchmark Observability

Date: 2026-03-21
Gate: Phase 09 benchmark observability integration

## Canonical Constants

- Classic Comet workspace: `zer0pa`
- Classic Comet project: `zpe-iot-performance`
- Opik workspace: `zer0pa`
- Opik project: `zpe-iot-performance`
- Opik host: `https://www.comet.com/opik/api`

## Code Surface

- `python/zpe_iot/tracking.py` now owns the shared create-or-verify adapter surface for Classic Comet and Opik.
- `validation/benchmarks/run_benchmarks.py` now instantiates the tracking bundle once per run, logs benchmark payloads through that bundle, and writes a compact tracking context artifact.
- `validation/destruct_tests/_common.py` now uses the same Classic Comet workspace and project constants instead of the drifted `zpe-iot` project name.
- `python/tests/test_tracking.py` verifies the no-credential fallback path.
- `python/pyproject.toml` now declares `opik>=1.10,<2.0` alongside the existing `comet_ml` dev dependency.

## Verification

1. Focused no-credential adapter test:
   - command: `PYTHONPATH=python:. /tmp/zpe-iot-phase5-arm64-venv/bin/python -m pytest -q -o addopts='' python/tests/test_tracking.py`
   - result: `1 passed`

2. Dependency import smoke:
   - command: `PYTHONPATH=python:. /tmp/zpe-iot-phase5-arm64-venv/bin/python -c "import comet_ml, opik, zpe_iot.tracking; print('imports_ok')"`
   - result: `imports_ok`
   - note: `opik` emits a Python 3.14 warning about Pydantic v1 compatibility, but import succeeds.

3. Benchmark runner integration without credentials:
   - command: `env -u COMET_API_KEY -u OPIK_API_KEY PYTHONPATH=python:. /tmp/zpe-iot-phase5-arm64-venv/bin/python -u validation/benchmarks/run_benchmarks.py`
   - result: benchmark runner completed and wrote:
     - `validation/results/benchmark_tracking_context_20260321T191046.json`
     - `validation/results/bench_summary_E1_real_public_20260321T191046.json`

## Measured Outcome

- `validation/results/benchmark_tracking_context_20260321T191046.json` records:
  - `classic_status = HOLD`
  - `opik_status = HOLD`
  - `classic_project = zpe-iot-performance`
  - `opik_project = zpe-iot-performance`
  - `opik_host = https://www.comet.com/opik/api`
  - notes:
    - `classic Comet adapter disabled by missing credential`
    - `Opik adapter disabled by missing credential`
- The benchmark authority surface still emitted normally on the same run:
  - `validation/results/bench_summary_E1_real_public_20260321T191046.json`
  - `mean CR = 17.163613932777356`
  - `wins = 10/11`

## Verdict

Phase 9 closes on the explicit local-fallback branch.

- The runner now uses one canonical workspace and one canonical project name family for both telemetry systems.
- Missing credentials no longer silently degrade into an alternate project surface.
- Live remote telemetry was not exercised in this session because `COMET_API_KEY` and `OPIK_API_KEY` were absent from the agent environment.

## Next Gate

Return to Phase 8 and resolve the `DS-11` authority-surface gap honestly. After that, rerun the benchmark runner with live credentials for the final gate if a remote Comet or Opik URL is required in Phase 10.
