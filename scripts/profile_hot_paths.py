#!/usr/bin/env python3
"""Profile encode/decode hot paths on E1 datasets."""

from __future__ import annotations

import cProfile
import io
import json
import pstats
import time
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from validation.benchmarks._common import ds_preset
from validation.datasets.loader import load_dataset
from zpe_iot import decode, encode

RESULTS_DIR = ROOT / "validation" / "results"
PERF_DOC_DIR = ROOT / "docs" / "perf"


def _run_windows(samples: np.ndarray, preset: str, repeats: int) -> tuple[list[float], list[float]]:
    samples = np.asarray(samples, dtype=np.float64)
    usable = (len(samples) // 256) * 256
    windows = samples[:usable].reshape(-1, 256)

    enc: list[float] = []
    dec: list[float] = []
    for _ in range(repeats):
        for w in windows:
            t0 = time.perf_counter()
            stream = encode(w, preset=preset)
            packet = stream.to_bytes()
            t1 = time.perf_counter()
            _ = decode(packet)
            t2 = time.perf_counter()
            enc.append((t1 - t0) * 1000.0)
            dec.append((t2 - t1) * 1000.0)
    return enc, dec


def main() -> int:
    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PERF_DOC_DIR.mkdir(parents=True, exist_ok=True)

    dataset_ids = [f"DS-{i:02d}" for i in range(1, 9)]
    rows: list[dict] = []

    profiler = cProfile.Profile()
    profiler.enable()

    for ds_id in dataset_ids:
        data = load_dataset(ds_id)
        samples = np.asarray(data["samples"], dtype=np.float64)[: 256 * 32]
        preset = ds_preset(ds_id)
        enc, dec = _run_windows(samples, preset=preset, repeats=5)
        rows.append(
            {
                "dataset": ds_id,
                "preset": preset,
                "encode_ms_mean": float(np.mean(enc) if enc else 0.0),
                "encode_ms_p50": float(np.percentile(enc, 50) if enc else 0.0),
                "encode_ms_p99": float(np.percentile(enc, 99) if enc else 0.0),
                "decode_ms_mean": float(np.mean(dec) if dec else 0.0),
                "decode_ms_p50": float(np.percentile(dec, 50) if dec else 0.0),
                "decode_ms_p99": float(np.percentile(dec, 99) if dec else 0.0),
                "windows_profiled": int(len(enc)),
            }
        )

    profiler.disable()

    stats_stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stats_stream).sort_stats("cumtime")
    stats.print_stats(30)

    profile_txt = PERF_DOC_DIR / f"profile_hot_paths_{ts}.txt"
    profile_txt.write_text(stats_stream.getvalue(), encoding="utf-8")

    summary = {
        "timestamp": ts,
        "datasets": rows,
        "artifacts": {
            "profile_text": str(profile_txt),
        },
    }
    profile_json = RESULTS_DIR / f"perf_profile_hot_paths_{ts}.json"
    profile_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"Saved: {profile_json}")
    print(f"Saved: {profile_txt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
