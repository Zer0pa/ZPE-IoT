#!/usr/bin/env python3
"""DT-02: Compression Floor (PRD §5.2 INV-COMPRESSION)."""

from __future__ import annotations

import numpy as np

from _common import available_or_skip, dataset_preset, ensure_datasets, log_result, print_case, safe_encode_decode, windows


def main() -> int:
    ensure_datasets()
    datasets = available_or_skip([f"DS-{i:02d}" for i in range(1, 11)])

    if not datasets:
        print_case("SKIP", "No datasets available")
        log_result("DT-02", "SKIPPED", {}, notes="No datasets")
        return 0

    hard_fail = False
    for ds in datasets:
        crs = []
        for w in windows(ds):
            stream, _ = safe_encode_decode(w, preset=dataset_preset(ds), mode="balanced")
            crs.append(stream.compression_ratio)

        min_cr = float(np.min(crs))
        mean_cr = float(np.mean(crs))

        if min_cr < 1.0:
            hard_fail = True
            print_case("FAIL", f"{ds} min CR={min_cr:.2f} < 1.0")
        else:
            print_case("PASS", f"{ds} min CR={min_cr:.2f} mean CR={mean_cr:.2f}")

        if ds in {f"DS-{i:02d}" for i in range(1, 9)} and mean_cr < 5.0:
            print_case("WARN", f"{ds} mean CR={mean_cr:.2f} < 5.0 target")

    log_result("DT-02", "PASS" if not hard_fail else "FAIL", {"dataset_count": len(datasets)})
    return 0 if not hard_fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
