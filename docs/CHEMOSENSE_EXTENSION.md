<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# Chemosense Extension

<p>
  <img src="../.github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

The chemosense stack adds deterministic smell+taste+touch+mental encoding and fusion to the Python SDK:

- `python/zpe_iot/chemosense/smell/`
- `python/zpe_iot/chemosense/taste/`
- `python/zpe_iot/chemosense/touch/`
- `python/zpe_iot/chemosense/mental/`
- `python/zpe_iot/chemosense/common/`
- `python/zpe_iot/chemosense/contract.py` (stable API contract layer)

## Encoding Domains

1. Mental (`0x0100` type bit)
2. Smell (`0x0200` type bit)
3. Taste (`0x0400` type bit)
4. Touch (`0x0800` type bit)

All payloads remain 20-bit word compatible. Mental uses mode2/mode3 wire lanes with contract-level contamination guards.

## Stable Runtime Entrypoints

- Python namespace: `zpe_iot.chemosense`
- CLI smoke path: `zpe-iot chemosense-smoke --json`
- Module path smoke: `python -m zpe_iot.cli chemosense-smoke --json`

### Contract Primitives

| Primitive | Purpose | Input | Output |
|---|---|---|---|
| `encode_smell_payload` | Schema-validated smell encode | smell payload dict | `list[int]` extension words |
| `decode_smell_payload` | Deterministic smell decode | `Iterable[int]` | `{\"metadata\": {...}, \"strokes\": [...]}` |
| `encode_taste_payload` | Schema-validated z-layer taste encode | taste payload dict | `list[int]` extension words |
| `decode_taste_payload` | Deterministic z-layer taste decode | `Iterable[int]` | `{\"metadata\": {...}, \"events\": [...]}` |
| `encode_touch_payload` | Schema-validated touch encode | touch payload dict | `list[int]` words |
| `decode_touch_payload` | Deterministic touch decode | `Iterable[int]` | `{\"metadata\": {...}, \"strokes\": [...]}` |
| `encode_mental_payload` | Schema-validated mental encode | mental payload dict | `list[int]` words |
| `decode_mental_payload` | Deterministic mental decode | `Iterable[int]` | `{\"metadata\": {...}, \"strokes\": [...]}` |
| `run_smoke_flow` | Canonical smoke primitive used by CLI | none | deterministic smoke payload dict |

### Error Surface

| Error Type | Trigger |
|---|---|
| `ChemosenseSchemaError` | Invalid payload schema (missing keys, wrong types/ranges) |
| `ChemosensePacketError` | Invalid or undecodable extension word streams |
| `ChemosenseError` | Base class for contract-layer failures |

## Payload Schemas

### Smell payload example

```json
{
  "metadata": { "sniff_hz": 3 },
  "strokes": [
    {
      "category": "FLORAL",
      "pleasantness_start": 4,
      "intensity_start": 1,
      "directions": [0, 2, 4]
    }
  ]
}
```

### Taste payload example

```json
{
  "adaptive": true,
  "events": [
    {
      "quality_vector": [7, 1, 1, 0, 3],
      "temporal_directions": [1, 1, 0, 0, 0, 7, 6, 6],
      "intensity_end": 4,
      "flavor_link": [1, 2]
    }
  ]
}
```

## Determinism and Safety

- Imports are local to `zpe_iot.chemosense.*` (no external source-tree dependency).
- CLI smoke path and Python smoke path both call `run_smoke_flow`, ensuring one semantic primitive.
- Taste temporal encoding supports coarse/fine adaptive mode with explicit decode metadata.
- Fusion scheduler preserves modality packet ordering (`taste -> smell -> touch`) and includes smell metadata words.
- Smoke flow uses canonical touch pack APIs (`touch_placeholder_removed: true`), not synthetic placeholder words.

## Validation Coverage

- `python/tests/test_chemosense.py`
- `python/tests/test_chemosense_extended.py`
- `python/tests/test_chemosense_contract.py`
- `python/tests/test_chemosense_touch.py`
- `python/tests/test_chemosense_mental.py`
- `python/tests/test_cli.py::test_cli_chemosense_smoke_json`

These tests validate roundtrip behavior, schema/error contracts, z-layer integrity, deterministic fused frame emission, import hygiene, and cross-modality contamination safety.

<p>
  <img src="../.github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>
