#!/usr/bin/env python3
"""Sweep threshold/mode and build Pareto frontier for CR vs NRMSE."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from zpe_iot import compute_nrmse, decode, encode


def load_samples(path: Path) -> np.ndarray:
    if path.suffix == ".npz":
        return np.asarray(np.load(path, allow_pickle=True)["samples"], dtype=np.float64)
    if path.suffix == ".csv":
        return np.loadtxt(path, delimiter=",", usecols=[-1], dtype=np.float64)
    raise ValueError("Input must be .npz or .csv")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "validation" / "results")
    args = parser.parse_args()

    samples = load_samples(args.input)
    if len(samples) > 50_000:
        samples = samples[:50_000]

    thresholds = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2]
    modes = ["fast", "balanced"]

    rows = []
    for mode in modes:
        for thr in thresholds:
            stream = encode(samples, preset="generic", mode=mode, threshold=thr)
            recon = decode(stream)
            rows.append(
                {
                    "mode": mode,
                    "threshold": thr,
                    "cr": stream.compression_ratio,
                    "nrmse": compute_nrmse(samples, recon),
                }
            )

    # Pareto frontier: maximize CR, minimize NRMSE
    rows_sorted = sorted(rows, key=lambda r: (r["nrmse"], -r["cr"]))
    frontier = []
    best_cr = -1.0
    for r in rows_sorted:
        if r["cr"] > best_cr:
            frontier.append(r)
            best_cr = r["cr"]

    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / f"pareto_frontier_{ts}.json"
    json_path.write_text(json.dumps({"rows": rows, "frontier": frontier}, indent=2))

    plt.figure(figsize=(8, 5))
    for mode in modes:
        pts = [r for r in rows if r["mode"] == mode]
        plt.scatter([p["nrmse"] for p in pts], [p["cr"] for p in pts], label=mode)
    plt.plot([p["nrmse"] for p in frontier], [p["cr"] for p in frontier], color="black", linewidth=1)
    plt.xlabel("NRMSE")
    plt.ylabel("Compression Ratio")
    plt.title("ZPE-IoT Pareto Frontier")
    plt.legend()
    png_path = args.output_dir / f"pareto_frontier_{ts}.png"
    plt.tight_layout()
    plt.savefig(png_path)

    best = max(frontier, key=lambda r: r["cr"] / max(r["nrmse"], 1e-9)) if frontier else None
    print(f"Saved {json_path}")
    print(f"Saved {png_path}")
    if best:
        print(f"Recommended config: mode={best['mode']} threshold={best['threshold']} cr={best['cr']:.2f} nrmse={best['nrmse']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
