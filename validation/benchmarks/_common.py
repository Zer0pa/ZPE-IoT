from __future__ import annotations

import json
import sys
import time
import tracemalloc
from datetime import datetime
from pathlib import Path
from typing import Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from validation.datasets.loader import list_available_datasets, load_dataset
from zpe_iot import compute_nrmse, decode, encode

RESULTS_DIR = ROOT / "validation" / "results"


def zpe_metrics(samples: np.ndarray, preset: str = "generic") -> dict:
    samples = np.asarray(samples, dtype=np.float64)
    usable = (len(samples) // 256) * 256
    windows = samples[:usable].reshape(-1, 256) if usable else samples.reshape(1, -1)

    crs = []
    errs = []
    enc_times = []
    dec_times = []

    tracemalloc.start()
    for w in windows:
        t0 = time.perf_counter()
        stream = encode(w, preset=preset)
        t1 = time.perf_counter()
        restored = decode(stream)
        t2 = time.perf_counter()

        crs.append(stream.compression_ratio)
        errs.append(compute_nrmse(w, restored))
        enc_times.append((t1 - t0) * 1000)
        dec_times.append((t2 - t1) * 1000)
    _cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "cr": float(np.mean(crs)),
        "nrmse": float(np.mean(errs)),
        "encode_ms": float(np.mean(enc_times)),
        "decode_ms": float(np.mean(dec_times)),
        "peak_bytes": int(peak),
    }


def run_competitor(samples: np.ndarray, compressor: Callable[[bytes], bytes], repeats: int = 10) -> dict:
    raw = np.asarray(samples, dtype=np.float64).tobytes()

    tracemalloc.start()
    times = []
    out = b""
    for _ in range(repeats):
        t0 = time.perf_counter()
        out = compressor(raw)
        times.append((time.perf_counter() - t0) * 1000)
    _cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "cr": float(len(raw) / max(1, len(out))),
        "encode_ms": float(np.mean(times)),
        "encode_p99_ms": float(np.percentile(times, 99)),
        "peak_bytes": int(peak),
        "compressed_bytes": len(out),
    }


def ds_preset(ds_id: str) -> str:
    mapping = {
        "DS-01": "generic",
        "DS-02": "vibration",
        "DS-03": "temperature",
        "DS-04": "accelerometer",
        "DS-05": "pressure",
        "DS-06": "generic",
        "DS-07": "gps_track",
        "DS-08": "voltage",
    }
    return mapping.get(ds_id, "generic")


def benchmark_dataset(ds_id: str, competitor_name: str, competitor_fn: Callable[[bytes], bytes]) -> dict:
    data = load_dataset(ds_id)
    samples = data["samples"][: 256 * 1000]
    zpe = zpe_metrics(samples, preset=ds_preset(ds_id))
    comp = run_competitor(samples, competitor_fn)

    winner = "zpe-iot" if zpe["cr"] > comp["cr"] else competitor_name
    return {
        "dataset": ds_id,
        "name": data["name"],
        "zpe_iot": zpe,
        competitor_name: comp,
        "winner": winner,
    }


def save_results(prefix: str, rows: list[dict]) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    path = RESULTS_DIR / f"{prefix}_{ts}.json"
    path.write_text(json.dumps({"timestamp": ts, "results": rows}, indent=2))
    return path


def available_sensor_datasets() -> list[str]:
    return [d for d in list_available_datasets() if d in {f"DS-{i:02d}" for i in range(1, 9)}]
