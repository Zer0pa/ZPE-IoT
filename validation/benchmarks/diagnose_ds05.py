#!/usr/bin/env python3
"""Inspect the live DS-05 chunk sink on the current packet surface."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from validation.datasets.loader import load_dataset
from zpe_iot import encode
from zpe_iot.codec import PACKET_MAGIC_ZERO_SPECIAL, pack_stream

WINDOW_SIZE = 256
MAX_WINDOWS = 64


def _windowed(samples: np.ndarray) -> np.ndarray:
    usable = min(len(samples) // WINDOW_SIZE, MAX_WINDOWS) * WINDOW_SIZE
    clipped = np.asarray(samples[:usable], dtype=np.float64)
    if usable == 0:
        raise RuntimeError("Need at least one full 256-sample window for DS-05 diagnosis")
    return clipped.reshape(-1, WINDOW_SIZE)


def _iter_chunks(rle_tokens):
    for d, m, count in rle_tokens:
        remaining = int(count)
        while remaining > 0:
            chunk = min(remaining, 127)
            yield int(d), int(m), chunk
            remaining -= chunk


def main() -> int:
    windows = _windowed(load_dataset("DS-05")["samples"])
    chunk_counter: Counter[tuple[int, int, int]] = Counter()
    total_chunks = 0
    baseline_bytes = 0
    candidate_bytes = 0
    switched_windows = 0

    for window in windows:
        stream = encode(window, preset="pressure")
        baseline_packet = pack_stream(stream, compact=True, zero_special=False)
        candidate_packet = stream.to_bytes()

        baseline_bytes += len(baseline_packet)
        candidate_bytes += len(candidate_packet)
        if candidate_packet[:2] == PACKET_MAGIC_ZERO_SPECIAL.to_bytes(2, "little"):
            switched_windows += 1

        for chunk in _iter_chunks(stream.rle_tokens):
            chunk_counter[chunk] += 1
            total_chunks += 1

    zero_count1 = sum(n for (d, m, count), n in chunk_counter.items() if d == 0 and m == 0 and count == 1)
    zero_runs = sum(n for (d, m, count), n in chunk_counter.items() if d == 0 and m == 0 and count > 1)

    payload = {
        "dataset": "DS-05",
        "preset": "pressure",
        "window_count": int(len(windows)),
        "chunk_count": total_chunks,
        "top_chunks": [
            {
                "chunk": [d, m, count],
                "count": n,
                "share": n / max(1, total_chunks),
            }
            for (d, m, count), n in chunk_counter.most_common(12)
        ],
        "zero_count1_chunk_share": zero_count1 / max(1, total_chunks),
        "zero_run_chunk_share": zero_runs / max(1, total_chunks),
        "baseline_total_bytes": baseline_bytes,
        "candidate_total_bytes": candidate_bytes,
        "candidate_byte_delta": candidate_bytes - baseline_bytes,
        "candidate_selected_windows": switched_windows,
        "candidate_selected_share": switched_windows / max(1, len(windows)),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
