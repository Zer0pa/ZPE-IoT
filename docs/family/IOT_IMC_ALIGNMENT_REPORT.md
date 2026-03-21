# IoT-IMC Alignment Report (Wave-1)

Date: 2026-03-21
Repo: `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot`

## Consumed IMC Freeze
- Contract: `/Users/Zer0pa/ZPE-IMC-REPO/v0.0/docs/family/IMC_INTERFACE_CONTRACT.md`
- Vector: `/Users/Zer0pa/ZPE-IMC-REPO/v0.0/docs/family/IMC_COMPATIBILITY_VECTOR.json`
- Release note: `/Users/Zer0pa/ZPE-IMC-REPO/v0.0/docs/family/IMC_RELEASE_NOTE_FOR_BIO_IOT.md`

## Verification
- `contract_version` consumed: `wave1.0`
- IMC vector SHA-256: `9c8b905f6c1d30d057955aa9adf0f7ff9139853494dca673e5fbe69f24fba10e`
- Result: PASS (matches frozen pin on the current March 21 local verification surface)

## Canonical Metric Authority
- Coordination authority is IMC compatibility vector canonical metric:
  - `canonical_demo_metrics.total_words = 844`
- IoT CLI or smoke variants are local diagnostics and not canonical for cross-family claims.

## IoT Wave-1 Compatibility Position
- IoT wire decode compatibility is held by packet-version assertions and golden packet fixtures (`python/tests/test_packet_compatibility.py`).
- Unsupported packet version handling is explicit and deterministic.
- Malformed packet rejection remains strict and non-silent.

## Divergence Boundaries
- IoT packet framing differs from IMC word-stream framing; alignment is contract-level, not byte-identical framing.
- Experimental wrappers (`WI-1`, `ZH-1`) remain feature-flagged and non-default in wave-1.
- Suite linkage is contract-based for private staging, not runtime-coupled to the IMC repo.

## Artifacts
- `docs/family/IOT_COMPATIBILITY_VECTOR.json`
- `docs/family/IOT_RELEASE_NOTE_FOR_COORDINATION.md`
- `validation/results/iot_wave1_phase5_alignment.txt`
- `proofs/FINAL_STATUS.md`
- `validation/results/release_preflight_report_20260321T205127.json`
