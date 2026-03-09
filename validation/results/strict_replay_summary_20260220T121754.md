# Strict Replay Summary (20260220T121754)

- Command: `python validation/destruct_tests/run_all_dts.py --strict-gates`
- Pinned interpreter: `/Users/prinivenpillay/ZPE IoT/zpe-iot/.venv/bin/python`
- Runs: 5
- Strict green 5/5: YES

| Run | RC | results_count | mandatory_failures | DT-09 status | DT-09 mean (ms) | DT-09 p99 (ms) | DT-10 | DT-11 | DT-22 | DT-27 |
|---:|---:|---:|---:|:---:|---:|---:|:---:|:---:|:---:|:---:|
| 1 | 0 | 27 | 0 | PASS | 0.268 | 0.283 | PASS | PASS | PASS | PASS |
| 2 | 0 | 27 | 0 | PASS | 0.268 | 0.299 | PASS | PASS | PASS | PASS |
| 3 | 0 | 27 | 0 | PASS | 0.271 | 0.302 | PASS | PASS | PASS | PASS |
| 4 | 0 | 27 | 0 | PASS | 0.295 | 0.478 | PASS | PASS | PASS | PASS |
| 5 | 0 | 27 | 0 | PASS | 0.463 | 1.884 | PASS | PASS | PASS | PASS |

## DT-09 Variance

- Gate mean ms: min=0.268, max=0.463, mean=0.313, stdev=0.076
- Gate p99 ms: min=0.283, max=1.884, mean=0.649, stdev=0.622
