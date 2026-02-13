#!/usr/bin/env python3
"""DT-03: Determinism. PASS if 10,000 seeded signals produce bit-identical output."""

from __future__ import annotations

import numpy as np

from _common import log_result, print_case
from zpe_iot import encode


def main() -> int:
    for seed in range(10_000):
        rng = np.random.default_rng(seed)
        x = rng.standard_normal(256)
        a = encode(x, preset="vibration", mode="balanced").to_bytes()
        b = encode(x, preset="vibration", mode="balanced").to_bytes()
        if a != b:
            print_case("FAIL", f"Seed {seed} produced non-deterministic output")
            log_result("DT-03", "FAIL", {"seed": seed})
            return 1
    print_case("PASS", "10,000 seeds deterministic")
    log_result("DT-03", "PASS", {"seeds": 10_000})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
