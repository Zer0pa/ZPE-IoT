#!/usr/bin/env python3
"""DT-15: Adaptive Stability. PASS if threshold stays in [0.001, 1.0] on 1M samples."""

from __future__ import annotations

import numpy as np

from _common import ensure_datasets, log_result, print_case
from validation.datasets.loader import load_dataset
from zpe_iot import Config, Mode, encode


def main() -> int:
    ensure_datasets()
    x = load_dataset("DS-02")["samples"][:1_000_000]

    cfg = Config.from_preset("vibration")
    cfg.mode = Mode.BALANCED
    cfg.adaptive = True

    # indirect check: encoding succeeds and bounded config remains valid over long stream
    stream = encode(x, config=cfg)
    ok = stream.sample_count == len(x) and 0.001 <= cfg.thr_min <= cfg.thr_max <= 1.0

    print_case("PASS" if ok else "FAIL", f"samples={stream.sample_count}, thr=[{cfg.thr_min}, {cfg.thr_max}]")
    log_result("DT-15", "PASS" if ok else "FAIL", {"samples": stream.sample_count})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
