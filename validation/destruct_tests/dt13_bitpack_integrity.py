#!/usr/bin/env python3
"""DT-13: Bitpack Integrity. PASS if pack->unpack round-trip is lossless on 10,000 streams."""

from __future__ import annotations

import numpy as np

from _common import log_result, print_case
from zpe_iot import EncodedStream, encode


def main() -> int:
    rng = np.random.default_rng(321)

    for i in range(10_000):
        x = rng.standard_normal(256)
        stream = encode(x, preset="generic")
        packet = stream.to_bytes()
        restored = EncodedStream.from_bytes(packet)

        if (
            stream.sample_count != restored.sample_count
            or stream.mode != restored.mode
            or abs(stream.step - restored.step) > 1e-4
            or stream.rle_tokens != restored.rle_tokens
        ):
            print_case("FAIL", f"Round-trip mismatch at i={i}")
            log_result("DT-13", "FAIL", {"index": i})
            return 1

    print_case("PASS", "10,000 streams round-trip lossless")
    log_result("DT-13", "PASS", {"streams": 10_000})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
