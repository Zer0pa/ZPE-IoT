#!/usr/bin/env python3
"""Compare zpe-iot vs Gorilla-style XOR+zlib proxy on all datasets."""

from __future__ import annotations

import numpy as np
import zlib

from _common import available_sensor_datasets, benchmark_dataset, save_results


def gorilla_proxy(raw: bytes) -> bytes:
    arr = np.frombuffer(raw, dtype=np.float64)
    bits = arr.view(np.uint64).copy()
    count = int(len(bits))
    if count == 0:
        return (0).to_bytes(4, "little")
    if count == 1:
        return (1).to_bytes(4, "little") + bits[:1].tobytes()
    xor = np.bitwise_xor(bits[1:], bits[:-1])
    return (
        count.to_bytes(4, "little")
        + bits[:1].tobytes()
        + zlib.compress(xor.tobytes(), level=6)
    )


def gorilla_proxy_decompress(blob: bytes) -> bytes:
    if len(blob) < 4:
        raise ValueError("gorilla blob too short")
    count = int.from_bytes(blob[:4], "little")
    if count == 0:
        return b""
    if len(blob) < 12:
        raise ValueError("gorilla blob missing seed value")
    seed = np.frombuffer(blob[4:12], dtype=np.uint64).copy()
    if count == 1:
        return seed.view(np.float64).tobytes()
    xor = np.frombuffer(zlib.decompress(blob[12:]), dtype=np.uint64)
    if len(xor) != count - 1:
        raise ValueError("gorilla xor length mismatch")
    out = np.empty(count, dtype=np.uint64)
    out[0] = seed[0]
    for i in range(1, count):
        out[i] = out[i - 1] ^ xor[i - 1]
    return out.view(np.float64).tobytes()


def main() -> int:
    rows = [
        benchmark_dataset(
            ds,
            "gorilla",
            gorilla_proxy,
            gorilla_proxy_decompress,
            repeats=5,
            warmup=1,
        )
        for ds in available_sensor_datasets()
    ]
    path = save_results(
        "bench_vs_gorilla",
        rows,
        method_metadata={
            "comparator": "gorilla_proxy_xor_zlib",
            "repeats": 5,
            "warmup": 1,
            "encode_decode_pathway": "zpe:wire_bytes, gorilla_proxy:raw_bytes",
        },
    )
    print(f"Saved {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
