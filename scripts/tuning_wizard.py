#!/usr/bin/env python3
"""Interactive tuning wizard for new sensor streams."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from zpe_iot import decode, encode
from zpe_iot.presets import all_presets


def load_signal(path: Path) -> np.ndarray:
    if path.suffix == ".npz":
        return np.asarray(np.load(path, allow_pickle=True)["samples"], dtype=np.float64)
    return np.loadtxt(path, delimiter=",", usecols=[-1], dtype=np.float64)


def main() -> int:
    print("ZPE-IoT Tuning Wizard")
    print("----------------------")
    sensor = input("What kind of sensor? [temperature/vibration/accelerometer/pressure/gps_track/voltage/current/flow/generic]: ").strip().lower()
    if sensor not in all_presets():
        sensor = "generic"

    sample_file = Path(input("Provide a sample file (.csv or .npz): ").strip())
    if not sample_file.exists():
        print("File does not exist.")
        return 1

    acceptable_error_pct = float(input("Acceptable error (% NRMSE)? [e.g. 5]: ").strip() or "5") / 100.0
    mode_pref = input("Output mode [fast/balanced]? ").strip().lower() or "balanced"
    if mode_pref not in {"fast", "balanced"}:
        mode_pref = "balanced"

    x = load_signal(sample_file)
    x = x[:50_000]

    candidates = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2]
    best = None
    for thr in candidates:
        s = encode(x, preset=sensor, mode=mode_pref, threshold=thr)
        y = decode(s)
        nrmse = float(np.sqrt(np.mean((x - y) ** 2)) / max(1e-9, np.max(x) - np.min(x)))
        if nrmse <= acceptable_error_pct:
            score = s.compression_ratio
            if best is None or score > best["compression_ratio"]:
                best = {
                    "preset": sensor,
                    "mode": mode_pref,
                    "threshold": thr,
                    "compression_ratio": s.compression_ratio,
                    "nrmse": nrmse,
                }

    if best is None:
        best = {"preset": sensor, "mode": mode_pref, "threshold": candidates[0], "compression_ratio": 0.0, "nrmse": 1.0}

    print(json.dumps(best, indent=2))
    out = ROOT / "validation" / "results" / "tuning_wizard_last.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(best, indent=2))
    print(f"Saved recommendation to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
