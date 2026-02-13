from __future__ import annotations

from pathlib import Path
from typing import Iterator

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT / "validation" / "datasets"


def load_dataset(ds_id: str) -> dict:
    """Load dataset by ID. Returns dict with 'samples', 'sample_rate', 'name'."""
    path = DATASETS_DIR / ds_id / "data.npz"
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {ds_id}")

    data = np.load(path, allow_pickle=True)
    return {
        "samples": np.asarray(data["samples"], dtype=np.float64),
        "sample_rate": float(np.asarray(data["sample_rate"]).reshape(-1)[0]),
        "name": str(np.asarray(data["name"]).reshape(-1)[0]),
        "provenance": str(np.asarray(data.get("provenance", ["unknown"]).reshape(-1))[0]),
    }


def list_available_datasets() -> list[str]:
    """Return list of downloaded dataset IDs."""
    if not DATASETS_DIR.exists():
        return []
    out = []
    for p in sorted(DATASETS_DIR.iterdir()):
        if p.is_dir() and p.name.startswith("DS-") and (p / "data.npz").exists():
            out.append(p.name)
    return out


def iter_dataset_windows(ds_id: str, window_size: int = 256) -> Iterator[np.ndarray]:
    """Yield non-overlapping windows from dataset."""
    data = load_dataset(ds_id)["samples"]
    n = len(data)
    for i in range(0, n - window_size + 1, window_size):
        yield data[i : i + window_size]
