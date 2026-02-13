#!/usr/bin/env python3
"""Compare zpe-iot vs zstandard (level 3) on all datasets."""

from __future__ import annotations

import zstandard as zstd

from _common import available_sensor_datasets, benchmark_dataset, save_results



def main() -> int:
    compressor = zstd.ZstdCompressor(level=3)
    rows = [benchmark_dataset(ds, "zstd", compressor.compress) for ds in available_sensor_datasets()]
    path = save_results("bench_vs_zstd", rows)
    print(f"Saved {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
