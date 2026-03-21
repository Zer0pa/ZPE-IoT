# Wheel Verification

Date: 2026-03-21
Phase: 03 portability, blind-clone, and wheel verification

## Objective

Verify that the current Python package builds a wheel and that a fresh environment can install, import, and exercise it without relying on source-tree imports.

## Wheel Build

Build workspace:

- source root: `/tmp/zpe-iot-phase3-clean.UhxVIC/repo/python`
- command: `python -m build --wheel`

Produced wheel:

- `/tmp/zpe-iot-phase3-clean.UhxVIC/repo/python/dist/zpe_iot-0.1.0-py3-none-any.whl`

## Cold Install Environment

- wheel venv: `/tmp/zpe-iot-phase3-wheel-venv`
- smoke workspace: `/tmp/zpe-iot-phase3-wheel-smoke`

The installed module resolved to:

- `/private/tmp/zpe-iot-phase3-wheel-venv/lib/python3.11/site-packages/zpe_iot/__init__.py`

That confirms the test ran from `site-packages`, not from the source tree.

## Cold-Wheel Smoke Result

The cold wheel environment passed all intended smoke checks:

- `zpe-iot compress`: PASS
- `zpe-iot info`: PASS
- `zpe-iot decompress`: PASS
- `zpe-iot diagnostics --json`: PASS
- `zpe-iot chemosense-smoke --json`: PASS

Representative outputs:

- sample smoke input: `256` rows
- packet size: `196` bytes
- compression ratio: `10.448979591836734x`
- diagnostics: `native_available = false`, `chemosense_available = true`
- chemosense smoke: `smell_stroke_count = 2`, `fused_event_count = 2`

## Honest Boundary

`VALD-03` is closed.

What this proves:

- the wheel can be built from the current code state
- a fresh environment can install and import it from `site-packages`
- the installed CLI smoke surface works without source-tree imports

What this does not claim:

- it does not claim the wheel bundles the Rust native library
- it does not claim cold-wheel parity for `_native`; the installed wheel currently exercises the pure-Python path with `native_available = false`
- it does not convert deferred publish into a completed publication claim
