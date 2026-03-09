# Chemosense Performance Profile

- Timestamp: `20260220T200249`
- Pathway: `encode_words_then_decode_words`
- Smell encode p50/p99: `1.368 / 1.471 ms`
- Smell decode p50/p99: `0.971 / 1.032 ms`
- Taste encode p50/p99: `3.395 / 3.491 ms`
- Taste decode p50/p99: `1.439 / 1.444 ms`

## Fusion Ingest Tightness
- Legacy ingest p50/p99: `3.373 / 3.665 ms`
- Current ingest p50/p99: `2.765 / 2.815 ms`
- Median latency improvement: `18.02%`
- Improvement gate (current < legacy): `True`

## Invariant Check
- Legacy packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
- Current packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
