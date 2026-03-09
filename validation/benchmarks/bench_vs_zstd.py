#!/usr/bin/env python3
"""Compare zpe-iot vs zstandard (level 3) on all datasets."""

from __future__ import annotations

import zstandard as zstd

from _common import available_sensor_datasets, benchmark_dataset, save_results



def main() -> int:
    compressor = zstd.ZstdCompressor(level=3)
    decompressor = zstd.ZstdDecompressor()
    rows = [
        benchmark_dataset(
            ds,
            "zstd",
            compressor.compress,
            decompressor.decompress,
            repeats=5,
            warmup=1,
        )
        for ds in available_sensor_datasets()
    ]
    path = save_results(
        "bench_vs_zstd",
        rows,
        method_metadata={
            "comparator": "zstd",
            "level": 3,
            "repeats": 5,
            "warmup": 1,
            "encode_decode_pathway": "zpe:wire_bytes, zstd:raw_bytes",
        },
    )
    print(f"Saved {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
