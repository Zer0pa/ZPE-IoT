#!/usr/bin/env python3
"""DT-07: Latch Freedom. PASS if 10M samples encode in <60s without exceptions."""

from __future__ import annotations

import time

import numpy as np

from _common import log_result, print_case
from zpe_iot import Config
from zpe_iot import encode
from zpe_iot import _native


def main() -> int:
    rng = np.random.default_rng(7)
    n_samples = 10_000_000
    window = 256
    t0 = time.perf_counter()
    if _native.available():
        # Use native Rust path for sustained-stream latch check in large chunks.
        cfg = Config.from_preset("generic")
        cfg.mode = "fast"
        chunk = 4096
        for _ in range(n_samples // chunk):
            x = rng.standard_normal(chunk)
            _native.encode(x, cfg)
    else:
        # Fallback path keeps the exact 10M workload but uses Python implementation.
        for _ in range(n_samples // window):
            x = rng.standard_normal(window)
            encode(x, preset="generic", mode="fast")
    elapsed = time.perf_counter() - t0

    ok = elapsed < 60.0
    print_case("PASS" if ok else "FAIL", f"Encoded 10M samples in {elapsed:.2f}s")
    log_result("DT-07", "PASS" if ok else "FAIL", {"elapsed_s": elapsed})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
