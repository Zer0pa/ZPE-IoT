#!/usr/bin/env python3
"""DT-08: DC Torture. PASS if no crash, finite output, CR>=1 for DC/extreme signals."""

from __future__ import annotations

import numpy as np

from _common import log_result, print_case
from zpe_iot import decode, encode


def main() -> int:
    cases = [
        np.zeros(2048),
        np.ones(2048),
        np.full(2048, 3.14),
        np.full(2048, 1e12),
    ]

    ok = True
    for i, x in enumerate(cases, start=1):
        try:
            stream = encode(x, preset="generic", mode="balanced")
            y = decode(stream)
            if stream.compression_ratio < 1.0 or not np.isfinite(y).all():
                ok = False
                print_case("FAIL", f"case={i}")
            else:
                print_case("PASS", f"case={i} CR={stream.compression_ratio:.2f}")
        except Exception as exc:
            ok = False
            print_case("FAIL", f"case={i} exception={exc}")

    log_result("DT-08", "PASS" if ok else "FAIL", {})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
