#!/usr/bin/env python3
"""Compare zpe-iot vs Gorilla-style XOR+zlib proxy on all datasets."""

from __future__ import annotations

import numpy as np
import zlib

from _common import available_sensor_datasets, benchmark_dataset, save_results


def gorilla_proxy(raw: bytes) -> bytes:
    # Lightweight Gorilla proxy: XOR adjacent float64 bit patterns and zlib the residual stream.
    arr = np.frombuffer(raw, dtype=np.float64)
    bits = arr.view(np.uint64)
    if len(bits) < 2:
        return raw
    xor = np.bitwise_xor(bits[1:], bits[:-1])
    return zlib.compress(xor.tobytes(), level=6)


def main() -> int:
    rows = [benchmark_dataset(ds, "gorilla", gorilla_proxy) for ds in available_sensor_datasets()]
    path = save_results("bench_vs_gorilla", rows)
    print(f"Saved {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
