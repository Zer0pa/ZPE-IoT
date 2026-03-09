# Chemosense Performance Profile

- Timestamp: `20260220T033607`
- Pathway: `encode_words_then_decode_words`
- Smell encode p50/p99: `1.266 / 1.268 ms`
- Smell decode p50/p99: `0.925 / 0.969 ms`
- Taste encode p50/p99: `3.170 / 3.292 ms`
- Taste decode p50/p99: `1.321 / 1.331 ms`

## Fusion Ingest Tightness
- Legacy ingest p50/p99: `3.128 / 3.164 ms`
- Current ingest p50/p99: `2.521 / 2.586 ms`
- Median latency improvement: `19.39%`
- Improvement gate (current < legacy): `True`

## Invariant Check
- Legacy packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
- Current packet counts: `{'taste_packets': 64, 'smell_packets': 64, 'touch_packets': 64, 'fused_events': 64}`
