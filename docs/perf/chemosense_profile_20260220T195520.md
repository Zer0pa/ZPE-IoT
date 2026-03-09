# Chemosense Performance Profile

- Timestamp: `20260220T195520`
- Pathway: `encode_words_then_decode_words`
- Smell encode p50/p99: `1.287 / 3.555 ms`
- Smell decode p50/p99: `0.915 / 1.051 ms`
- Taste encode p50/p99: `2.984 / 3.122 ms`
- Taste decode p50/p99: `1.352 / 1.355 ms`

## Fusion Ingest Tightness
- Legacy ingest p50/p99: `3.198 / 3.301 ms`
- Current ingest p50/p99: `2.586 / 2.675 ms`
- Median latency improvement: `19.12%`
- Improvement gate (current < legacy): `True`

## Invariant Check
- Legacy packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
- Current packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
