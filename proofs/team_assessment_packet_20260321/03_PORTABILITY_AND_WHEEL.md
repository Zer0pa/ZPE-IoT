# Portability And Wheel

Date: 2026-03-21

## Clean-Workspace Reproduction

The source tree was copied into an equivalently clean `/tmp` workspace without `.git`, prior `validation/results`, build outputs, or release bundles.

Inside that clean workspace:

- source install passed
- `zpe-iot compress`, `info`, `decompress`, `diagnostics`, and `chemosense-smoke` all passed
- the decisive portability DT subset ended at `5 PASS`, `0 FAIL` on `DT-10`, `DT-11`, `DT-13`, `DT-17`, and `DT-25`

Important finding:

- the first clean-room DT run exposed two hidden assumptions:
  - `DT-11` required a local Rust build in that workspace
  - `DT-25` required generation of a compact Chemosense benchmark-summary artifact if `validation/results` was intentionally omitted

Those assumptions were then satisfied inside the clean workspace itself, and the rerun passed. This is a real portability close, not a dev-lane carry-over.

## Cold Wheel Verification

The wheel built successfully as:

- `python/dist/zpe_iot-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`

In a separate fresh venv, the installed module resolved to `site-packages`, not the source tree, and the installed CLI passed:

- `compress`
- `info`
- `decompress`
- `diagnostics`
- `chemosense-smoke`

## Claim Boundary

Portability is closed for this PRD, but the exact wording matters:

- clean-room source install and targeted validation are verified
- cold wheel build/install/import smoke is verified
- the local arm64 macOS wheel is native-bundled and cold install exposes `native_available = true`
- multi-platform publication is still not claimed

That boundary is acceptable for the current requirement set and must remain explicit in any external description.
