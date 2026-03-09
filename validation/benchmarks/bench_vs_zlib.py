#!/usr/bin/env python3
"""Compare zpe-iot vs zlib (level 6) on all datasets."""

from __future__ import annotations

import zlib

from _common import available_sensor_datasets, benchmark_dataset, save_results


def main() -> int:
    rows = [
        benchmark_dataset(
            ds,
            "zlib",
            lambda b: zlib.compress(b, level=6),
            zlib.decompress,
            repeats=5,
            warmup=1,
        )
        for ds in available_sensor_datasets()
    ]
    path = save_results(
        "bench_vs_zlib",
        rows,
        method_metadata={
            "comparator": "zlib",
            "level": 6,
            "repeats": 5,
            "warmup": 1,
            "encode_decode_pathway": "zpe:wire_bytes, zlib:raw_bytes",
        },
    )
    print(f"Saved {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
