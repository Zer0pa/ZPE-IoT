# Strict Replay Summary (20260220T114632)

- Command: `python validation/destruct_tests/run_all_dts.py --strict-gates`
- Pinned interpreter: `/Users/prinivenpillay/ZPE IoT/zpe-iot/.venv/bin/python`
- Runs: 5
- Strict green 5/5: NO

| Run | RC | results_count | mandatory_failures | DT-09 status | DT-09 mean (ms) | DT-09 p99 (ms) | DT-10 | DT-11 | DT-22 | DT-27 |
|---:|---:|---:|---:|:---:|---:|---:|:---:|:---:|:---:|:---:|
| 1 | 1 | 27 | 1 | FAIL | 0.652 | 0.961 | PASS | PASS | PASS | PASS |
| 2 | 0 | 27 | 0 | PASS | 0.339 | 0.359 | PASS | PASS | PASS | PASS |
| 3 | 0 | 27 | 0 | PASS | 0.306 | 0.316 | PASS | PASS | PASS | PASS |
| 4 | 0 | 27 | 0 | PASS | 0.274 | 0.337 | PASS | PASS | PASS | PASS |
| 5 | 0 | 27 | 0 | PASS | 0.284 | 0.343 | PASS | PASS | PASS | PASS |

## DT-09 Variance

- Gate mean ms: min=0.274, max=0.652, mean=0.371, stdev=0.142
- Gate p99 ms: min=0.316, max=0.961, mean=0.463, stdev=0.249
