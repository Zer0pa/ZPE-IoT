#!/usr/bin/env python3
"""Probe why WI-1 and ZH-1 violate DT-10 on the DS-02 strict-gate surface."""

from __future__ import annotations

import json
import os
import sys
import zlib
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from validation.datasets.loader import load_dataset
from zpe_iot import encode
from zpe_iot.codec import _delta_encode_bytes, _maybe_wrap_wi1, _maybe_wrap_zh1

OUT_PATH = ROOT / "proofs" / "artifacts" / "PHASE2_MONOTONICITY_PROBE_20260320.json"
THRESHOLDS = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]
PROBE_THRESHOLDS = [0.1, 0.2, 0.5]
ZLIB_LEVELS = list(range(1, 10))


@contextmanager
def _flag(key: str, enabled: bool):
    old = os.getenv(key)
    try:
        if enabled:
            os.environ[key] = "1"
        else:
            os.environ.pop(key, None)
        yield
    finally:
        if old is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = old


def _dt10_series(samples, flag_name: str) -> list[float]:
    with _flag(flag_name, True):
        return [
            float(encode(samples, preset="vibration", threshold=thr, mode="balanced").compression_ratio)
            for thr in THRESHOLDS
        ]


def _fullstream_packets(samples) -> dict[float, bytes]:
    packets: dict[float, bytes] = {}
    for thr in PROBE_THRESHOLDS:
        with _flag("ZPE_IOT_WI1_ENTROPY_STAGE", False), _flag("ZPE_IOT_ZH1_DERIVATIVE_STAGE", False):
            packets[thr] = encode(samples, preset="vibration", threshold=thr, mode="balanced").to_bytes()
    return packets


def _wi1_probe(samples) -> dict:
    packets = _fullstream_packets(samples)
    dt10_crs = _dt10_series(samples, "ZPE_IOT_WI1_ENTROPY_STAGE")

    fullstream = []
    for thr in PROBE_THRESHOLDS:
        packet = packets[thr]
        with _flag("ZPE_IOT_WI1_ENTROPY_STAGE", True):
            wrapped = _maybe_wrap_wi1(packet)
        fullstream.append(
            {
                "threshold": thr,
                "raw_len": len(packet),
                "wrapped_len": len(wrapped),
                "wrapped": len(wrapped) < len(packet),
                "cr": (len(samples) * 8) / len(wrapped),
            }
        )

    level_sweep = {}
    for level in ZLIB_LEVELS:
        level_sweep[str(level)] = {
            str(thr): len(zlib.compress(packets[thr], level=level)) + 8 for thr in PROBE_THRESHOLDS
        }

    return {
        "flag": "ZPE_IOT_WI1_ENTROPY_STAGE",
        "dt10_thresholds": THRESHOLDS,
        "dt10_crs": dt10_crs,
        "fullstream_probe": fullstream,
        "zlib_level_sweep": level_sweep,
        "monotonic_breaks": [
            {
                "from_threshold": THRESHOLDS[i],
                "to_threshold": THRESHOLDS[i + 1],
                "from_cr": dt10_crs[i],
                "to_cr": dt10_crs[i + 1],
            }
            for i in range(len(THRESHOLDS) - 1)
            if dt10_crs[i + 1] + 1e-9 < dt10_crs[i]
        ],
        "level_tuning_survives_failure": all(
            level_sweep[str(level)]["0.2"] > level_sweep[str(level)]["0.1"] for level in ZLIB_LEVELS
        ),
    }


def _zh1_probe(samples) -> dict:
    packets = _fullstream_packets(samples)
    dt10_crs = _dt10_series(samples, "ZPE_IOT_ZH1_DERIVATIVE_STAGE")

    fullstream = []
    for thr in PROBE_THRESHOLDS:
        packet = packets[thr]
        with _flag("ZPE_IOT_ZH1_DERIVATIVE_STAGE", True):
            wrapped = _maybe_wrap_zh1(packet)
        fullstream.append(
            {
                "threshold": thr,
                "raw_len": len(packet),
                "wrapped_len": len(wrapped),
                "wrapped": len(wrapped) < len(packet),
                "cr": (len(samples) * 8) / len(wrapped),
            }
        )

    level_sweep = {}
    for level in ZLIB_LEVELS:
        level_sweep[str(level)] = {
            str(thr): len(zlib.compress(_delta_encode_bytes(packets[thr]), level=level)) + 8
            for thr in PROBE_THRESHOLDS
        }

    return {
        "flag": "ZPE_IOT_ZH1_DERIVATIVE_STAGE",
        "dt10_thresholds": THRESHOLDS,
        "dt10_crs": dt10_crs,
        "fullstream_probe": fullstream,
        "zlib_level_sweep": level_sweep,
        "monotonic_breaks": [
            {
                "from_threshold": THRESHOLDS[i],
                "to_threshold": THRESHOLDS[i + 1],
                "from_cr": dt10_crs[i],
                "to_cr": dt10_crs[i + 1],
            }
            for i in range(len(THRESHOLDS) - 1)
            if dt10_crs[i + 1] + 1e-9 < dt10_crs[i]
        ],
        "level_tuning_survives_failure": all(
            level_sweep[str(level)]["0.2"] > level_sweep[str(level)]["0.1"] for level in ZLIB_LEVELS
        ),
    }


def main() -> int:
    samples = load_dataset("DS-02")["samples"][:20_480]
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "dataset": "DS-02",
        "sample_count": int(len(samples)),
        "preset": "vibration",
        "workstreams": {
            "WI-1": _wi1_probe(samples),
            "ZH-1": _zh1_probe(samples),
        },
        "verdict": {
            "summary": (
                "Both experimental packet-wrapper workstreams remain DT-10 failures after the native parity fix. "
                "For both families, the full-stream wrapped packet grows from threshold 0.1 to 0.2 across zlib "
                "levels 1-9, so the monotonicity break survives simple compression-level retuning."
            )
        },
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Saved: {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
