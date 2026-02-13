#!/usr/bin/env python3
"""DT-10: Monotonicity. PASS if CR is non-decreasing with threshold sweep."""

from __future__ import annotations

import numpy as np

from _common import ensure_datasets, log_result, print_case
from validation.datasets.loader import load_dataset
from zpe_iot import encode


def main() -> int:
    ensure_datasets()
    x = load_dataset("DS-02")["samples"][:20_480]

    thresholds = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]
    crs = []
    for thr in thresholds:
        stream = encode(x, preset="vibration", threshold=thr, mode="balanced")
        crs.append(stream.compression_ratio)

    ok = all(crs[i] <= crs[i + 1] + 1e-9 for i in range(len(crs) - 1))
    print_case("PASS" if ok else "FAIL", f"thresholds={thresholds} crs={[round(v, 3) for v in crs]}")
    log_result("DT-10", "PASS" if ok else "FAIL", {"cr_start": crs[0], "cr_end": crs[-1]})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
