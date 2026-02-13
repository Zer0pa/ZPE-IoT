#!/usr/bin/env python3
"""DT-11: Cross-Platform Parity. PASS if Python and Rust native packets match for 100 vectors."""

from __future__ import annotations

import numpy as np

from _common import log_result, print_case
from zpe_iot import Config, encode
from zpe_iot import _native


def main() -> int:
    if not _native.available():
        print_case("FAIL", "Native library unavailable")
        log_result("DT-11", "FAIL", {"native_available": 0})
        return 1

    rng = np.random.default_rng(123)
    cfg = Config.from_preset("vibration")
    for i in range(100):
        x = rng.standard_normal(256)
        py_packet = encode(x, config=cfg).to_bytes()
        rs_packet = _native.encode(x, config=cfg)
        if py_packet != rs_packet:
            print_case("FAIL", f"Mismatch on vector {i}")
            log_result("DT-11", "FAIL", {"vector": i})
            return 1

    print_case("PASS", "100 vectors bit-identical")
    log_result("DT-11", "PASS", {"vectors": 100})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
