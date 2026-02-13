#!/usr/bin/env python3
"""DT-01: Fidelity Gate (PRD §5.2 INV-FIDELITY). PASS if max NRMSE < 5% per dataset."""

from __future__ import annotations

import numpy as np

from _common import (
    available_or_skip,
    dataset_preset,
    ensure_datasets,
    log_result,
    metric_summary,
    print_case,
    safe_encode_decode,
    windows,
)


def main() -> int:
    ensure_datasets()
    datasets = available_or_skip([f"DS-{i:02d}" for i in range(1, 9)])

    if not datasets:
        print_case("SKIP", "No datasets available")
        log_result("DT-01", "SKIPPED", {}, notes="No datasets")
        return 0

    overall_pass = True
    report = {}

    for ds in datasets:
        errs = []
        ds_windows = windows(ds)
        ds_range = float(np.max(ds_windows) - np.min(ds_windows)) if len(ds_windows) else 1.0
        for w in ds_windows:
            preset = dataset_preset(ds)
            _, recon = safe_encode_decode(w, preset=preset, mode="balanced")
            err = float(np.sqrt(np.mean((w - recon) ** 2)) / max(1e-9, ds_range))
            errs.append(err)

        stats = metric_summary(errs)
        report[ds] = stats
        if stats["max"] >= 0.05:
            overall_pass = False
            print_case("FAIL", f"{ds} max NRMSE={stats['max']:.4f} >= 0.05")
        else:
            print_case("PASS", f"{ds} mean={stats['mean']:.4f} p95={stats['p95']:.4f} max={stats['max']:.4f}")

    log_result("DT-01", "PASS" if overall_pass else "FAIL", {"datasets": len(datasets)}, notes=str(report))
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
