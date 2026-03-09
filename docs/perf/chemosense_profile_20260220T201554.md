# Chemosense Performance Profile

- Timestamp: `20260220T201554`
- Pathway: `encode_words_then_decode_words`
- Smell encode p50/p99: `1.259 / 1.280 ms`
- Smell decode p50/p99: `0.907 / 0.936 ms`
- Taste encode p50/p99: `2.978 / 3.278 ms`
- Taste decode p50/p99: `1.326 / 1.337 ms`

## Fusion Ingest Tightness
- Legacy ingest p50/p99: `3.117 / 3.280 ms`
- Current ingest p50/p99: `2.552 / 2.718 ms`
- Median latency improvement: `18.14%`
- Improvement gate (current < legacy): `True`

## Invariant Check
- Legacy packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
- Current packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
