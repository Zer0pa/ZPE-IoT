#!/usr/bin/env python3
"""Run all benchmark comparators and aggregate a summary table."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "validation" / "results"

SCRIPTS = [
    "bench_vs_zstd.py",
    "bench_vs_lz4.py",
    "bench_vs_zlib.py",
    "bench_vs_gorilla.py",
]


def _latest(prefix: str) -> Path | None:
    files = sorted(RESULTS_DIR.glob(f"{prefix}_*.json"))
    return files[-1] if files else None


def main() -> int:
    for script in SCRIPTS:
        cmd = [sys.executable, str(Path(__file__).resolve().parent / script)]
        print(f"[RUN] {' '.join(cmd)}")
        subprocess.run(cmd, check=True, cwd=str(ROOT))

    latest = {
        "zstd": _latest("bench_vs_zstd"),
        "lz4": _latest("bench_vs_lz4"),
        "zlib": _latest("bench_vs_zlib"),
        "gorilla": _latest("bench_vs_gorilla"),
    }

    for key, path in latest.items():
        if path is None:
            raise RuntimeError(f"Missing benchmark output for {key}")

    zstd_rows = {r["dataset"]: r for r in json.loads(latest["zstd"].read_text())["results"]}
    lz4_rows = {r["dataset"]: r for r in json.loads(latest["lz4"].read_text())["results"]}
    zlib_rows = {r["dataset"]: r for r in json.loads(latest["zlib"].read_text())["results"]}
    gor_rows = {r["dataset"]: r for r in json.loads(latest["gorilla"].read_text())["results"]}

    datasets = sorted(set(zstd_rows) & set(lz4_rows) & set(zlib_rows) & set(gor_rows))
    summary = []
    wins = 0

    for ds in datasets:
        zpe_cr = zstd_rows[ds]["zpe_iot"]["cr"]
        row = {
            "dataset": ds,
            "zpe_iot_cr": zpe_cr,
            "zpe_iot_nrmse": zstd_rows[ds]["zpe_iot"]["nrmse"],
            "zstd_cr": zstd_rows[ds]["zstd"]["cr"],
            "lz4_cr": lz4_rows[ds]["lz4"]["cr"],
            "zlib_cr": zlib_rows[ds]["zlib"]["cr"],
            "gorilla_cr": gor_rows[ds]["gorilla"]["cr"],
        }
        row["winner"] = "zpe-iot" if zpe_cr > max(row["zstd_cr"], row["lz4_cr"], row["zlib_cr"], row["gorilla_cr"]) else "competitor"
        wins += 1 if row["winner"] == "zpe-iot" else 0
        summary.append(row)

    mean_cr = sum(r["zpe_iot_cr"] for r in summary) / max(1, len(summary))
    pt6_pass = wins > (len(summary) / 2)

    payload = {
        "timestamp": datetime.now().strftime("%Y%m%dT%H%M%S"),
        "datasets": summary,
        "wins": wins,
        "total": len(summary),
        "pt6_pass": pt6_pass,
        "mean_cr": mean_cr,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"bench_summary_{payload['timestamp']}.json"
    out.write_text(json.dumps(payload, indent=2))

    print(f"Saved summary: {out}")
    print(f"PT-6 {'PASS' if pt6_pass else 'FAIL'} ({wins}/{len(summary)} wins)")

    return 0 if pt6_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
