"""Compress a CSV sensor log file.

Usage:
  python csv_compressor.py input.csv output.zpk
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import zpe_iot


def read_values(path: Path) -> np.ndarray:
    values = []
    with path.open() as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            try:
                values.append(float(row[-1]))
            except ValueError:
                continue
    return np.asarray(values, dtype=np.float64)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python csv_compressor.py input.csv output.zpk")
        return 1

    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    signal = read_values(in_path)
    stream = zpe_iot.encode(signal, preset="generic")
    out_path.write_bytes(stream.to_bytes())

    raw_bytes = signal.nbytes
    packed = stream.packed_size
    savings = 1.0 - (packed / max(1, raw_bytes))

    print(f"Original bytes: {raw_bytes}")
    print(f"Compressed bytes: {packed}")
    print(f"Compression ratio: {stream.compression_ratio:.2f}x")
    print(f"Savings: {savings:.1%}")
    print(f"Estimated cellular savings (1MB/day/device @ $1/MB): ${(365 - 365/stream.compression_ratio):.2f}/device/year")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
