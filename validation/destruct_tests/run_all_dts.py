#!/usr/bin/env python3
"""
Master DT runner. Execute all destruct tests and report pass/fail.

Usage:
  python run_all_dts.py
  python run_all_dts.py --priority P0
  python run_all_dts.py --dt 1 5 15
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DT_DIR = Path(__file__).resolve().parent
ROOT = DT_DIR.parents[1]
RESULTS_DIR = ROOT / "validation" / "results"

DT_PRIORITY = {
    1: "P0",
    2: "P0",
    3: "P0",
    4: "P0",
    5: "P0",
    6: "P0",
    7: "P0",
    8: "P1",
    9: "P1",
    10: "P1",
    11: "P1",
    12: "P1",
    13: "P1",
    14: "P1",
    15: "P1",
    16: "P2",
}

DT_NAMES = {
    1: "Fidelity Gate",
    2: "Compression Floor",
    3: "Determinism",
    4: "Noise Robustness",
    5: "Pathological Inputs",
    6: "RAM Budget",
    7: "Latch Freedom",
    8: "DC Torture",
    9: "Latency",
    10: "Monotonicity",
    11: "Cross-Platform Parity",
    12: "Preset Coverage",
    13: "Bitpack Integrity",
    14: "CRC Detection",
    15: "Adaptive Stability",
    16: "Benchmark Regression",
}


def find_dt_script(dt_num: int) -> Path | None:
    prefix = f"dt{dt_num:02d}_"
    scripts = sorted(DT_DIR.glob(f"{prefix}*.py"))
    if not scripts:
        return None
    return scripts[0]


def run_dt(dt_num: int) -> dict:
    script = find_dt_script(dt_num)
    if script is None or "placeholder" in script.name:
        return {
            "dt": dt_num,
            "name": DT_NAMES.get(dt_num, "Unknown"),
            "priority": DT_PRIORITY.get(dt_num, "?"),
            "status": "NOT_IMPLEMENTED",
            "output": "",
            "returncode": None,
        }

    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=3600,
            cwd=str(ROOT),  # zpe-iot root
        )
        status = "PASS" if result.returncode == 0 else "FAIL"
        stdout = (result.stdout + result.stderr).strip()
        if "[SKIP]" in stdout and status == "PASS":
            status = "SKIPPED"
        return {
            "dt": dt_num,
            "name": DT_NAMES.get(dt_num, "Unknown"),
            "priority": DT_PRIORITY.get(dt_num, "?"),
            "status": status,
            "output": stdout[-4000:],
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "dt": dt_num,
            "name": DT_NAMES.get(dt_num, "Unknown"),
            "priority": DT_PRIORITY.get(dt_num, "?"),
            "status": "TIMEOUT",
            "output": "Exceeded timeout (3600s)",
            "returncode": None,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--priority", choices=["P0", "P1", "P2"], default=None)
    parser.add_argument("--dt", nargs="+", type=int, default=None)
    args = parser.parse_args()

    dts_to_run = list(range(1, 17))
    if args.dt:
        dts_to_run = args.dt
    elif args.priority:
        dts_to_run = [n for n in dts_to_run if DT_PRIORITY.get(n) == args.priority]

    print(f"{'DT':>4}  {'Name':<26} {'Pri':>3}  {'Status':<12}")
    print("-" * 56)

    results = []
    emoji = {"PASS": "OK", "FAIL": "XX", "NOT_IMPLEMENTED": "--", "TIMEOUT": "TT", "SKIPPED": "SK"}

    for dt_num in dts_to_run:
        r = run_dt(dt_num)
        results.append(r)
        print(f"{r['dt']:>4}  {r['name']:<26} {r['priority']:>3}  {r['status']:<12} {emoji.get(r['status'], '??')}")

    print("-" * 56)
    counts = {k: sum(1 for r in results if r["status"] == k) for k in ["PASS", "FAIL", "SKIPPED", "NOT_IMPLEMENTED", "TIMEOUT"]}
    print("Summary:", ", ".join(f"{k}={v}" for k, v in counts.items()))

    p0_bad = [r for r in results if r["priority"] == "P0" and r["status"] in {"FAIL", "TIMEOUT", "NOT_IMPLEMENTED"}]
    if p0_bad:
        print("\nWARNING: P0 gate failed. DO NOT proceed to next phase.")
        for r in p0_bad:
            print(f"  DT-{r['dt']:02d} {r['name']}: {r['status']}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"dt_results_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    with out_path.open("w") as f:
        json.dump({"timestamp": datetime.now(timezone.utc).isoformat(), "results": results}, f, indent=2)
    print(f"\nSaved: {out_path}")

    return 1 if any(r["status"] in {"FAIL", "TIMEOUT"} for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
