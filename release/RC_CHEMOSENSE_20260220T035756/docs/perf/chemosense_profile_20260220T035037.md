# Chemosense Performance Profile

- Timestamp: `20260220T035037`
- Pathway: `encode_words_then_decode_words`
- Smell encode p50/p99: `1.275 / 1.436 ms`
- Smell decode p50/p99: `0.995 / 1.018 ms`
- Taste encode p50/p99: `3.282 / 3.518 ms`
- Taste decode p50/p99: `1.321 / 1.559 ms`

## Fusion Ingest Tightness
- Legacy ingest p50/p99: `3.589 / 3.803 ms`
- Current ingest p50/p99: `2.901 / 3.092 ms`
- Median latency improvement: `19.18%`
- Improvement gate (current < legacy): `True`

## Invariant Check
- Legacy packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
- Current packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
