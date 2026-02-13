#!/usr/bin/env python3
"""DT-14: CRC Detection. PASS if >99.9% corrupted packets detected."""

from __future__ import annotations

import numpy as np

from _common import log_result, print_case
from zpe_iot import EncodedStream, encode


def corrupt(packet: bytearray, rng: np.random.Generator, multi: bool) -> bytes:
    p = bytearray(packet)
    n_bits = 2 if multi else 1
    for _ in range(n_bits):
        bit_idx = int(rng.integers(0, (len(p) - 2) * 8))  # avoid flipping crc field directly
        byte_idx = bit_idx // 8
        p[byte_idx] ^= 1 << (bit_idx % 8)
    return bytes(p)


def main() -> int:
    rng = np.random.default_rng(99)
    trials = 1000
    corrupted = int(trials * 0.15)
    detected = 0

    base_packets = []
    for _ in range(trials):
        x = rng.standard_normal(256)
        base_packets.append(bytearray(encode(x, preset="generic").to_bytes()))

    for i in range(corrupted):
        packet = base_packets[i]
        bad = corrupt(packet, rng, multi=(i >= int(corrupted * 0.67)))
        try:
            EncodedStream.from_bytes(bad)
        except Exception:
            detected += 1

    rate = detected / corrupted if corrupted else 1.0
    ok = rate > 0.999
    print_case("PASS" if ok else "FAIL", f"CRC detection rate={rate:.4%} ({detected}/{corrupted})")
    log_result("DT-14", "PASS" if ok else "FAIL", {"crc_detection_rate": rate})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
