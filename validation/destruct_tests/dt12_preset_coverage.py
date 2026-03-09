#!/usr/bin/env python3
"""DT-12: Preset Coverage. PASS if each preset meets ratified E1 floors."""

from __future__ import annotations

import numpy as np

from _common import ensure_datasets, log_result, print_case, windows
from thresholds import PRESET_MAX_MEAN_NRMSE, PRESET_MIN_MEAN_CR
from validation.datasets.loader import list_available_datasets
from validation.metrics.fidelity import FidelityMode, fidelity_label, nrmse
from zpe_iot import decode, encode

MAPPING = {
    "temperature": "DS-03",
    "vibration": "DS-02",
    "accelerometer": "DS-04",
    "pressure": "DS-05",
    "gps_track": "DS-07",
    "voltage": "DS-08",
    "current": "DS-08",
    "flow": "DS-03",
    "generic": "DS-06",
}
DT12_MODE = FidelityMode.WINDOW_NORMALIZED


def main() -> int:
    ensure_datasets()
    available = set(list_available_datasets())
    ok = True

    for preset, ds in MAPPING.items():
        if ds not in available:
            print_case("SKIP", f"{preset} skipped (missing {ds})")
            continue

        crs = []
        errs = []
        for w in windows(ds, max_windows=200):
            s = encode(w, preset=preset)
            y = decode(s)
            crs.append(s.compression_ratio)
            errs.append(nrmse(w, y, mode=DT12_MODE))

        mean_cr = float(np.mean(crs))
        mean_err = float(np.mean(errs))
        pass_case = mean_cr >= PRESET_MIN_MEAN_CR and mean_err < PRESET_MAX_MEAN_NRMSE
        print_case(
            "PASS" if pass_case else "FAIL",
            f"{preset}: mean CR={mean_cr:.2f}, mean {fidelity_label(DT12_MODE)}={mean_err:.4f}",
        )
        ok = ok and pass_case

    log_result("DT-12", "PASS" if ok else "FAIL", {})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
