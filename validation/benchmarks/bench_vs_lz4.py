#!/usr/bin/env python3
"""Compare zpe-iot vs LZ4 on all datasets."""

from __future__ import annotations

import lz4.frame

from _common import available_sensor_datasets, benchmark_dataset, save_results


def main() -> int:
    rows = [benchmark_dataset(ds, "lz4", lz4.frame.compress) for ds in available_sensor_datasets()]
    path = save_results("bench_vs_lz4", rows)
    print(f"Saved {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
