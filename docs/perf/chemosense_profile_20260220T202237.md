# Chemosense Performance Profile

- Timestamp: `20260220T202237`
- Pathway: `encode_words_then_decode_words`
- Smell encode p50/p99: `1.242 / 1.269 ms`
- Smell decode p50/p99: `0.871 / 0.925 ms`
- Taste encode p50/p99: `2.937 / 3.067 ms`
- Taste decode p50/p99: `1.306 / 1.312 ms`

## Fusion Ingest Tightness
- Legacy ingest p50/p99: `3.048 / 3.168 ms`
- Current ingest p50/p99: `2.493 / 2.608 ms`
- Median latency improvement: `18.23%`
- Improvement gate (current < legacy): `True`

## Invariant Check
- Legacy packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
- Current packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
