# Chemosense Performance Profile

- Timestamp: `20260309T060912`
- Pathway: `encode_words_then_decode_words`
- Smell encode p50/p99: `1.245 / 1.462 ms`
- Smell decode p50/p99: `0.885 / 0.889 ms`
- Taste encode p50/p99: `2.936 / 3.168 ms`
- Taste decode p50/p99: `1.322 / 1.331 ms`

## Fusion Ingest Tightness
- Legacy ingest p50/p99: `3.121 / 3.270 ms`
- Current ingest p50/p99: `2.562 / 2.759 ms`
- Median latency improvement: `17.89%`
- Improvement gate (current < legacy): `True`

## Invariant Check
- Legacy packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
- Current packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
