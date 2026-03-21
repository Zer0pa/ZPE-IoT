from __future__ import annotations

import json
import platform
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
from validation.metrics.fidelity import FidelityMode, fidelity_label, nrmse
from zpe_iot import decode, encode

RESULTS_DIR = ROOT / "validation" / "results"
MANIFEST = ROOT / "validation" / "datasets" / "manifest.json"
BENCHMARK_FIDELITY_MODE = FidelityMode.WINDOW_NORMALIZED


def _mean(values: list[float]) -> float:
    return float(np.mean(values)) if values else 0.0


def _p(values: list[float], q: float) -> float:
    return float(np.percentile(values, q)) if values else 0.0


def zpe_metrics(samples: np.ndarray, preset: str = "generic", repeats: int = 5, warmup: int = 1) -> dict:
    samples = np.asarray(samples, dtype=np.float64)
    usable = (len(samples) // 256) * 256
    windows = samples[:usable].reshape(-1, 256) if usable else samples.reshape(1, -1)

    crs = []
    errs = []
    enc_times = []
    dec_times = []
    raw_total_bytes = 0
    payload_total_bytes = 0

    tracemalloc.start()
    total_runs = max(0, int(warmup)) + max(1, int(repeats))
    for run_idx in range(total_runs):
        measure = run_idx >= max(0, int(warmup))
        for w in windows:
            t0 = time.perf_counter()
            stream = encode(w, preset=preset)
            packet = stream.to_bytes()
            t1 = time.perf_counter()
            restored = decode(packet)
            t2 = time.perf_counter()

            if measure:
                raw_bytes = len(w) * 8
                payload_bytes = len(packet)
                raw_total_bytes += raw_bytes
                payload_total_bytes += payload_bytes
                crs.append(raw_bytes / max(1, payload_bytes))
                errs.append(nrmse(w, restored, mode=BENCHMARK_FIDELITY_MODE))
                enc_times.append((t1 - t0) * 1000.0)
                dec_times.append((t2 - t1) * 1000.0)
    _cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    relative_reduction_vs_raw_pct = (
        (1.0 - (payload_total_bytes / raw_total_bytes)) * 100.0 if raw_total_bytes else 0.0
    )

    return {
        "cr": _mean(crs),
        "nrmse": _mean(errs),
        "encode_ms": _mean(enc_times),
        "decode_ms": _mean(dec_times),
        "encode_p50_ms": _p(enc_times, 50),
        "encode_p99_ms": _p(enc_times, 99),
        "decode_p50_ms": _p(dec_times, 50),
        "decode_p99_ms": _p(dec_times, 99),
        "peak_bytes": int(peak),
        "iterations": max(1, int(repeats)),
        "warmup_iterations": max(0, int(warmup)),
        "pathway": "wire_bytes_encode_then_decode_bytes",
        "raw_bytes": int(raw_total_bytes),
        "transport_payload_bytes": int(payload_total_bytes),
        "relative_reduction_vs_raw_pct": float(relative_reduction_vs_raw_pct),
        "fidelity_mode": BENCHMARK_FIDELITY_MODE.value,
        "fidelity_label": fidelity_label(BENCHMARK_FIDELITY_MODE),
    }


def run_competitor(
    samples: np.ndarray,
    compressor: Callable[[bytes], bytes],
    decompressor: Callable[[bytes], bytes],
    repeats: int = 5,
    warmup: int = 1,
) -> dict:
    raw = np.asarray(samples, dtype=np.float64).tobytes()

    tracemalloc.start()
    enc_times = []
    dec_times = []
    out = b""
    total_runs = max(0, int(warmup)) + max(1, int(repeats))
    for run_idx in range(total_runs):
        measure = run_idx >= max(0, int(warmup))
        t0 = time.perf_counter()
        out = compressor(raw)
        t1 = time.perf_counter()
        restored = decompressor(out)
        t2 = time.perf_counter()
        if restored != raw:
            raise RuntimeError("Comparator decode mismatch in fairness envelope")
        if measure:
            enc_times.append((t1 - t0) * 1000.0)
            dec_times.append((t2 - t1) * 1000.0)
    _cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    raw_bytes = len(raw)
    payload_bytes = len(out)
    relative_reduction_vs_raw_pct = (1.0 - (payload_bytes / raw_bytes)) * 100.0 if raw_bytes else 0.0

    return {
        "cr": float(raw_bytes / max(1, payload_bytes)),
        "encode_ms": _mean(enc_times),
        "decode_ms": _mean(dec_times),
        "encode_p50_ms": _p(enc_times, 50),
        "encode_p99_ms": _p(enc_times, 99),
        "decode_p50_ms": _p(dec_times, 50),
        "decode_p99_ms": _p(dec_times, 99),
        "peak_bytes": int(peak),
        "compressed_bytes": payload_bytes,
        "raw_bytes": raw_bytes,
        "transport_payload_bytes": payload_bytes,
        "relative_reduction_vs_raw_pct": float(relative_reduction_vs_raw_pct),
        "iterations": max(1, int(repeats)),
        "warmup_iterations": max(0, int(warmup)),
        "pathway": "raw_bytes_encode_then_decode_bytes",
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
        "DS-09": "vibration",
        "DS-10": "accelerometer",
        "DS-11": "generic",
        "DS-12": "voltage",
    }
    return mapping.get(ds_id, "generic")


def benchmark_dataset(
    ds_id: str,
    competitor_name: str,
    competitor_compress: Callable[[bytes], bytes],
    competitor_decompress: Callable[[bytes], bytes],
    repeats: int = 5,
    warmup: int = 1,
) -> dict:
    data = load_dataset(ds_id)
    samples = data["samples"][: 256 * 64]
    zpe = zpe_metrics(samples, preset=ds_preset(ds_id), repeats=repeats, warmup=warmup)
    comp = run_competitor(samples, competitor_compress, competitor_decompress, repeats=repeats, warmup=warmup)

    winner = "zpe-iot" if zpe["cr"] > comp["cr"] else competitor_name
    return {
        "dataset": ds_id,
        "name": data["name"],
        "zpe_iot": zpe,
        competitor_name: comp,
        "winner": winner,
        "method": {
            "repeats": max(1, int(repeats)),
            "warmup": max(0, int(warmup)),
            "zpe_pathway": "wire_bytes_encode_then_decode_bytes",
            "baseline_pathway": "raw_bytes_encode_then_decode_bytes",
            "fidelity_mode": BENCHMARK_FIDELITY_MODE.value,
            "fidelity_label": fidelity_label(BENCHMARK_FIDELITY_MODE),
        },
    }


def save_results(prefix: str, rows: list[dict], method_metadata: dict | None = None) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    path = RESULTS_DIR / f"{prefix}_{ts}.json"
    payload = {
        "timestamp": ts,
        "results": rows,
        "method_metadata": method_metadata
        or {
            "encode_decode_pathway": "zpe:wire_bytes, baselines:raw_bytes",
            "warmup_iterations": rows[0].get("method", {}).get("warmup", 0) if rows else 0,
            "iteration_count": rows[0].get("method", {}).get("repeats", 0) if rows else 0,
            "hardware_profile": {
                "machine": platform.machine(),
                "processor": platform.processor(),
                "platform": platform.platform(),
            },
        },
    }
    path.write_text(json.dumps(payload, indent=2))
    return path


def available_sensor_datasets() -> list[str]:
    if not MANIFEST.exists():
        return list_available_datasets()

    manifest = json.loads(MANIFEST.read_text())
    ready: list[str] = []
    for ds_id in list_available_datasets():
        entry = manifest.get(ds_id, {})
        if not ds_id.startswith("DS-"):
            continue
        if str(entry.get("status", "READY")).upper() != "READY":
            continue
        ready.append(ds_id)
    return ready
