#!/usr/bin/env python3
"""Run a customer-specific side-by-side compression report in <5 minutes."""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
import zlib
from datetime import datetime
from pathlib import Path

import lz4.frame
import numpy as np
import zstandard as zstd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from zpe_iot import compute_nrmse, decode, encode


def load_values(path: Path) -> np.ndarray:
    if path.suffix == ".npz":
        return np.asarray(np.load(path, allow_pickle=True)["samples"], dtype=np.float64)
    return np.loadtxt(path, delimiter=",", usecols=[-1], dtype=np.float64)


def _mean(values: list[float]) -> float:
    return float(np.mean(values)) if values else 0.0


def _p(values: list[float], q: float) -> float:
    return float(np.percentile(values, q)) if values else 0.0


def bench_competitor(raw: bytes, compress_fn, decompress_fn, repeats: int = 5, warmup: int = 1) -> dict:
    enc_ms: list[float] = []
    dec_ms: list[float] = []
    out = b""
    total_runs = max(0, warmup) + max(1, repeats)
    for run_idx in range(total_runs):
        measure = run_idx >= max(0, warmup)
        t0 = time.perf_counter()
        out = compress_fn(raw)
        t1 = time.perf_counter()
        restored = decompress_fn(out)
        t2 = time.perf_counter()
        if restored != raw:
            raise RuntimeError("Comparator decode mismatch during fairness run")
        if measure:
            enc_ms.append((t1 - t0) * 1000.0)
            dec_ms.append((t2 - t1) * 1000.0)

    cr = (len(raw) / max(1, len(out))) if out is not None else 0.0
    return {
        "compressed_bytes": int(len(out)),
        "compression_ratio": float(cr),
        "encode_ms_mean": _mean(enc_ms),
        "decode_ms_mean": _mean(dec_ms),
        "encode_ms_p50": _p(enc_ms, 50),
        "encode_ms_p99": _p(enc_ms, 99),
        "decode_ms_p50": _p(dec_ms, 50),
        "decode_ms_p99": _p(dec_ms, 99),
        "repeats": max(1, repeats),
        "warmup": max(0, warmup),
    }


def bench_zpe(samples: np.ndarray, preset: str, repeats: int = 5, warmup: int = 1) -> dict:
    x = np.asarray(samples, dtype=np.float64)
    enc_ms: list[float] = []
    dec_ms: list[float] = []
    errs: list[float] = []
    crs: list[float] = []
    packed_sizes: list[int] = []

    total_runs = max(0, warmup) + max(1, repeats)
    for run_idx in range(total_runs):
        measure = run_idx >= max(0, warmup)
        t0 = time.perf_counter()
        stream = encode(x, preset=preset)
        packet = stream.to_bytes()
        t1 = time.perf_counter()
        y = decode(packet)
        t2 = time.perf_counter()

        if measure:
            enc_ms.append((t1 - t0) * 1000.0)
            dec_ms.append((t2 - t1) * 1000.0)
            errs.append(float(compute_nrmse(x, y)))
            crs.append(float((x.nbytes) / max(1, len(packet))))
            packed_sizes.append(int(len(packet)))

    return {
        "compressed_bytes": int(np.mean(packed_sizes) if packed_sizes else 0),
        "compression_ratio": _mean(crs),
        "nrmse": _mean(errs),
        "encode_ms": _mean(enc_ms),
        "decode_ms": _mean(dec_ms),
        "encode_ms_p50": _p(enc_ms, 50),
        "encode_ms_p99": _p(enc_ms, 99),
        "decode_ms_p50": _p(dec_ms, 50),
        "decode_ms_p99": _p(dec_ms, 99),
        "repeats": max(1, repeats),
        "warmup": max(0, warmup),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=Path)
    parser.add_argument("--preset", default="generic")
    parser.add_argument("--cost-per-mb", type=float, default=1.0)
    parser.add_argument("--max-samples", type=int, default=65_535)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    args = parser.parse_args()

    x = load_values(args.input_file)
    x = x[: min(args.max_samples, 65_535)]
    raw = x.astype(np.float64).tobytes()

    repeats = max(1, args.repeats)
    warmup = max(0, args.warmup)
    zpe = bench_zpe(x, preset=args.preset, repeats=repeats, warmup=warmup)

    zstd_comp = zstd.ZstdCompressor(level=3)
    zstd_dec = zstd.ZstdDecompressor()
    comparators = {
        "zstd": bench_competitor(raw, zstd_comp.compress, zstd_dec.decompress, repeats=repeats, warmup=warmup),
        "lz4": bench_competitor(raw, lz4.frame.compress, lz4.frame.decompress, repeats=repeats, warmup=warmup),
        "zlib": bench_competitor(raw, lambda b: zlib.compress(b, level=6), zlib.decompress, repeats=repeats, warmup=warmup),
    }

    raw_bytes = len(raw)
    annual_before = (raw_bytes / (1024 * 1024)) * args.cost_per_mb * 365
    annual_after = annual_before / max(zpe["compression_ratio"], 1.0)

    for name, met in comparators.items():
        met["annual_cost_after"] = float(annual_before / max(met["compression_ratio"], 1.0))
        met["annual_savings_vs_raw"] = float(annual_before - met["annual_cost_after"])

    report = {
        "timestamp": datetime.now().isoformat(),
        "input": str(args.input_file),
        "preset": args.preset,
        "samples": int(len(x)),
        "raw_bytes": int(raw_bytes),
        "cost_per_mb": float(args.cost_per_mb),
        "zpe_iot": {
            **zpe,
            "annual_cost_before": float(annual_before),
            "annual_cost_after": float(annual_after),
            "annual_savings": float(annual_before - annual_after),
        },
        "comparators": comparators,
        "winner_by_cr": "zpe-iot"
        if zpe["compression_ratio"] > max(v["compression_ratio"] for v in comparators.values())
        else max(comparators, key=lambda k: comparators[k]["compression_ratio"]),
        "report_type": "side_by_side_baseline_comparison",
        "method_metadata": {
            "measurement_envelope": "all codecs measured as encode+decode over identical float64 raw bytes",
            "zpe_pathway": "encode(samples)->packet bytes; decode(packet bytes)",
            "baseline_pathway": "compress(raw bytes); decompress(compressed bytes)",
            "repeats": repeats,
            "warmup": warmup,
            "hardware_profile": {
                "machine": platform.machine(),
                "processor": platform.processor(),
                "platform": platform.platform(),
            },
        },
    }

    out = ROOT / "validation" / "results" / f"customer_demo_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(f"Saved report to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
