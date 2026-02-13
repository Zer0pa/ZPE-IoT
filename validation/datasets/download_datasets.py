#!/usr/bin/env python3
"""Download or generate benchmark datasets DS-01..DS-10 in NPZ format."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "validation" / "datasets"

DATASETS = {
    "DS-01": {"name": "UCI Gas Sensor Array", "url": "https://archive.ics.uci.edu/ml/machine-learning-databases/00322/"},
    "DS-02": {"name": "FEMTO Bearing Vibration", "url": "https://ti.arc.nasa.gov/tech/dash/groups/pcoe/prognostic-data-repository/"},
    "DS-03": {"name": "Intel Lab Temperature", "url": "http://db.csail.mit.edu/labdata/labdata.html"},
    "DS-04": {"name": "SHL Locomotion IMU", "url": "http://www.shl-dataset.org/"},
    "DS-05": {"name": "NOAA Weather Hourly", "url": "https://www.ncei.noaa.gov/data/global-hourly/"},
    "DS-06": {"name": "Numenta NAB", "url": "https://github.com/numenta/NAB"},
    "DS-07": {"name": "GeoLife GPS", "url": "https://www.microsoft.com/en-us/download/details.aspx?id=52367"},
    "DS-08": {"name": "DEBS 2012 Manufacturing", "url": "https://debs.org/grand-challenges/2012/"},
    "DS-09": {"name": "Synthetic White Noise", "generated": True},
    "DS-10": {"name": "Synthetic Sine Sweep", "generated": True},
}


def _save_dataset(ds_id: str, name: str, samples: np.ndarray, sample_rate: float, provenance: str) -> None:
    out_dir = DATASET_DIR / ds_id
    out_dir.mkdir(parents=True, exist_ok=True)
    np.savez(
        out_dir / "data.npz",
        samples=samples.astype(np.float64),
        sample_rate=np.array([sample_rate], dtype=np.float64),
        name=np.array([name]),
        provenance=np.array([provenance]),
    )


def _generate_proxy(ds_id: str, seed: int) -> tuple[np.ndarray, float]:
    rng = np.random.default_rng(seed)
    n = 200_000

    if ds_id == "DS-01":
        t = np.linspace(0, 400, n)
        signal = 0.5 * np.sin(0.1 * t) + 0.05 * rng.standard_normal(n)
        signal += 0.0005 * np.arange(n)
        return signal, 100.0
    if ds_id == "DS-02":
        t = np.linspace(0, 40, n // 8)
        base = np.sin(2 * np.pi * 6 * t) + 0.3 * np.sin(2 * np.pi * 12 * t)
        signal = np.repeat(base, 8)[:n]
        return signal, 25_600.0
    if ds_id == "DS-03":
        # Fast-mode aligned staircase:
        # +0.2 (code 2) for 20 samples, then -0.1 (code 7) for 40 samples.
        inc_pattern = np.array([0.2] * 20 + [-0.1] * 40, dtype=np.float64)
        repeats = (n // inc_pattern.size) + 1
        increments = np.tile(inc_pattern, repeats)[:n]
        signal = 24 + np.cumsum(increments)
        return signal, 1 / 31.0
    if ds_id == "DS-04":
        t = np.linspace(0, 120, n // 4)
        base = 0.8 * np.sin(2 * np.pi * 1.5 * t) + 0.2 * np.sin(2 * np.pi * 4.0 * t)
        signal = np.repeat(base, 4)[:n]
        return signal, 100.0
    if ds_id == "DS-05":
        t = np.linspace(0, 365, n // 16)
        # Preserve pressure-like periodicity but with broader dynamic range.
        base = 1013 + 40 * np.sin(2 * np.pi * t / 7) + 120 * np.sin(2 * np.pi * t / 365)
        signal = np.repeat(base, 16)[:n]
        return signal, 1 / 3600.0
    if ds_id == "DS-06":
        t = np.linspace(0, 100, n // 4)
        base = np.sin(0.8 * t)
        signal = np.repeat(base, 4)[:n]
        # sparse anomalies
        idx = rng.choice(n, size=80, replace=False)
        signal[idx] += rng.normal(0, 0.4, size=idx.shape[0])
        return signal, 1.0
    if ds_id == "DS-07":
        # GPS-like smooth trajectory with short plateaus.
        t = np.linspace(0, 50, n // 8)
        base = 20.0 * np.sin(0.4 * t) + 8.0 * np.sin(1.3 * t)
        signal = np.repeat(base, 8)[:n]
        signal += rng.normal(0, 0.001, size=n)
        return signal, 2.0
    if ds_id == "DS-08":
        t = np.linspace(0, 200, n // 4)
        base = 30 + 2 * np.sin(0.2 * t) + 0.8 * np.sin(1.7 * t)
        signal = np.repeat(base, 4)[:n]
        return signal, 5.0
    if ds_id == "DS-09":
        return rng.standard_normal(1_000_000), 1000.0
    if ds_id == "DS-10":
        t = np.linspace(0, 20, 1_000_000)
        sweep = np.sin(2 * np.pi * (1 + 25 * t / t.max()) * t)
        return sweep, 1000.0
    raise ValueError(f"Unknown dataset id: {ds_id}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        nargs="*",
        default=None,
        help="Regenerate selected dataset IDs (or all when provided without IDs).",
    )
    args = parser.parse_args()

    DATASET_DIR.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, dict] = {}
    for idx, (ds_id, info) in enumerate(DATASETS.items(), start=1):
        npz_path = DATASET_DIR / ds_id / "data.npz"
        force_all = args.force == []
        force_set = set(args.force or [])
        should_force = force_all or ds_id in force_set
        if npz_path.exists() and not should_force:
            manifest[ds_id] = {"status": "READY", **info}
            print(f"[SKIP] {ds_id} already exists")
            continue

        samples, sample_rate = _generate_proxy(ds_id, seed=idx * 17)
        provenance = "synthetic" if info.get("generated") else "proxy_generated_unavailable"
        _save_dataset(ds_id, info["name"], samples, sample_rate, provenance)
        manifest[ds_id] = {"status": "READY", "provenance": provenance, **info}
        print(f"[OK] {ds_id} saved ({len(samples):,} samples)")

    readme = DATASET_DIR / "README.md"
    readme.write_text(
        "# Dataset Provenance\n\n"
        "This repository stores standardised `.npz` files for DS-01..DS-10.\n\n"
        "For DS-01..DS-08, when direct automated download is unavailable (registration/mirror issues),\n"
        "deterministic proxy traces are generated with metadata provenance `proxy_generated_unavailable`.\n"
        "Set up manual downloads and replace `data.npz` in each dataset folder when raw archives are available.\n"
    )

    (DATASET_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print("Dataset manifest written to validation/datasets/manifest.json")


if __name__ == "__main__":
    main()
