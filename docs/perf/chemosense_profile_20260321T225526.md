# Chemosense Performance Profile

- Timestamp: `20260321T225526`
- Pathway: `encode_words_then_decode_words`
- Smell encode p50/p99: `0.588 / 0.593 ms`
- Smell decode p50/p99: `0.449 / 0.453 ms`
- Taste encode p50/p99: `1.393 / 1.399 ms`
- Taste decode p50/p99: `0.647 / 0.649 ms`

## Fusion Ingest Tightness
- Legacy ingest p50/p99: `1.534 / 1.539 ms`
- Current ingest p50/p99: `1.282 / 1.303 ms`
- Median latency improvement: `16.43%`
- Improvement gate (current < legacy): `True`

## Invariant Check
- Legacy packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
- Current packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
