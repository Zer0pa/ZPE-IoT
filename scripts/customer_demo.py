#!/usr/bin/env python3
"""Run a customer-specific compression report in <5 minutes."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from zpe_iot import compute_nrmse, decode, encode


def load_values(path: Path) -> np.ndarray:
    if path.suffix == ".npz":
        return np.asarray(np.load(path, allow_pickle=True)["samples"], dtype=np.float64)
    return np.loadtxt(path, delimiter=",", usecols=[-1], dtype=np.float64)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=Path)
    parser.add_argument("--preset", default="generic")
    parser.add_argument("--cost-per-mb", type=float, default=1.0)
    args = parser.parse_args()

    x = load_values(args.input_file)
    x = x[:200_000]

    stream = encode(x, preset=args.preset)
    y = decode(stream)

    raw_bytes = x.nbytes
    packed_bytes = stream.packed_size
    cr = stream.compression_ratio
    nrmse = compute_nrmse(x, y)

    annual_before = (raw_bytes / (1024 * 1024)) * args.cost_per_mb * 365
    annual_after = annual_before / max(cr, 1.0)

    report = {
        "timestamp": datetime.now().isoformat(),
        "input": str(args.input_file),
        "preset": args.preset,
        "samples": int(len(x)),
        "raw_bytes": int(raw_bytes),
        "compressed_bytes": int(packed_bytes),
        "compression_ratio": float(cr),
        "nrmse": float(nrmse),
        "annual_cost_before": float(annual_before),
        "annual_cost_after": float(annual_after),
        "annual_savings": float(annual_before - annual_after),
    }

    out = ROOT / "validation" / "results" / f"customer_demo_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print(f"Saved report to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
