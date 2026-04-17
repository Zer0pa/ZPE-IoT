<p>
  <img src="../../.github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# IoT-IMC Alignment Report (Wave-1)

Date: 2026-03-21
Repository URL: `https://github.com/Zer0pa/ZPE-IoT`

<p>
  <img src="../../.github/assets/readme/section-bars/family-alignment.svg" alt="FAMILY ALIGNMENT" width="100%">
</p>

## Consumed IMC Freeze
- Contract: `https://github.com/Zer0pa/ZPE-IMC/blob/main/v0.0/docs/family/IMC_INTERFACE_CONTRACT.md`
- Vector: `https://github.com/Zer0pa/ZPE-IMC/blob/main/v0.0/docs/family/IMC_COMPATIBILITY_VECTOR.json`
- Release note: `https://github.com/Zer0pa/ZPE-IMC/blob/main/v0.0/docs/family/IMC_RELEASE_NOTE_FOR_BIO_IOT.md`

<p>
  <img src="../../.github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

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
- IMC acts as a coordination contract for this repo, not as a shared runtime substrate.
- Suite linkage is contract-based for always-in-beta coordination, not runtime-coupled to the IMC repo.

## Artifacts
- `docs/family/IOT_COMPATIBILITY_VECTOR.json`
- `docs/family/IOT_RELEASE_NOTE_FOR_COORDINATION.md`
- `validation/results/iot_wave1_phase5_alignment.txt`
- `validation/results/IOT_WAVE1_RELEASE_READINESS_REPORT.md`
- `validation/results/release_preflight_report_20260321T205127.json`

<p>
  <img src="../../.github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>
