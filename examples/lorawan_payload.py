"""Fit a short temperature window into the LoRaWAN DR0 payload budget."""

from __future__ import annotations

import json

import numpy as np
import zpe_iot


MAX_LORAWAN_DR0_BYTES = 51


def build_lorawan_window(sample_count: int = 24) -> np.ndarray:
    t = np.linspace(0.0, 2 * np.pi, sample_count, dtype=np.float64)
    return 21.2 + 0.08 * np.sin(t)


def encode_lorawan_payload(samples: np.ndarray | None = None) -> bytes:
    window = build_lorawan_window() if samples is None else np.asarray(samples, dtype=np.float64)
    return zpe_iot.encode(window, preset="temperature").to_bytes()


def summarize_lorawan_payload() -> dict:
    samples = build_lorawan_window()
    packet = encode_lorawan_payload(samples)
    restored = zpe_iot.decode(packet)
    return {
        "sample_count": int(samples.size),
        "packet_bytes": len(packet),
        "budget_bytes": MAX_LORAWAN_DR0_BYTES,
        "fits_budget": len(packet) <= MAX_LORAWAN_DR0_BYTES,
        "compression_ratio": float((samples.size * 8) / max(1, len(packet))),
        "nrmse": float(zpe_iot.compute_nrmse(samples, restored)),
    }


def main() -> int:
    print(json.dumps(summarize_lorawan_payload(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
