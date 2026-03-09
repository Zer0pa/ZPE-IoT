#!/usr/bin/env python3
"""Compare zpe-iot vs LZ4 on all datasets."""

from __future__ import annotations

import lz4.frame

from _common import available_sensor_datasets, benchmark_dataset, save_results


def main() -> int:
    rows = [
        benchmark_dataset(
            ds,
            "lz4",
            lz4.frame.compress,
            lz4.frame.decompress,
            repeats=5,
            warmup=1,
        )
        for ds in available_sensor_datasets()
    ]
    path = save_results(
        "bench_vs_lz4",
        rows,
        method_metadata={
            "comparator": "lz4",
            "repeats": 5,
            "warmup": 1,
            "encode_decode_pathway": "zpe:wire_bytes, lz4:raw_bytes",
        },
    )
    print(f"Saved {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
