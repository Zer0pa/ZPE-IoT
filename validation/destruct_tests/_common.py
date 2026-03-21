from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PYTHON_DIR = ROOT / "python"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from zpe_iot import Config, compute_nrmse, decode, encode
from zpe_iot.presets import all_presets
from zpe_iot.tracking import DEFAULT_CLASSIC_PROJECT, DEFAULT_WORKSPACE

from validation.datasets.loader import iter_dataset_windows, list_available_datasets, load_dataset

SESSION_LOG = ROOT / "docs" / "SESSION_LOG.md"

DATASET_PRESET = {
    "DS-01": "generic",
    "DS-02": "vibration",
    "DS-03": "temperature",
    "DS-04": "accelerometer",
    "DS-05": "pressure",
    "DS-06": "generic",
    "DS-07": "gps_track",
    "DS-08": "temperature",
    "DS-09": "generic",
    "DS-10": "vibration",
}


def ensure_datasets() -> None:
    available = set(list_available_datasets())
    required = {f"DS-{i:02d}" for i in range(1, 11)}
    if not required.issubset(available):
        script = ROOT / "validation" / "datasets" / "download_datasets.py"
        os.system(f"{sys.executable} {script}")


def windows(ds_id: str, max_windows: int | None = None, random_sample: bool = False, seed: int = 0):
    arr = np.array(list(iter_dataset_windows(ds_id)), dtype=np.float64)
    if arr.size == 0:
        return []
    if max_windows is None or len(arr) <= max_windows:
        return arr
    if random_sample:
        rng = np.random.default_rng(seed)
        idx = rng.choice(len(arr), size=max_windows, replace=False)
        return arr[idx]
    return arr[:max_windows]


def dataset_preset(ds_id: str) -> str:
    return DATASET_PRESET.get(ds_id, "generic")


def log_result(dt_name: str, status: str, metrics: dict, params: dict | None = None, notes: str = "") -> None:
    params = params or {}
    ts = datetime.now(timezone.utc).isoformat()

    try:
        if os.getenv("ZPE_IOT_COMET_OFFLINE") == "1":
            raise RuntimeError("Comet offline forced")
        import comet_ml  # type: ignore

        exp = comet_ml.Experiment(
            project_name=DEFAULT_CLASSIC_PROJECT,
            workspace=DEFAULT_WORKSPACE,
            auto_metric_logging=False,
        )
        exp.set_name(f"{dt_name.lower()}-{datetime.now().strftime('%Y%m%dT%H%M%S')}")
        for k, v in metrics.items():
            exp.log_metric(k, float(v) if isinstance(v, (int, float, np.floating)) else 0)
        for k, v in params.items():
            exp.log_parameter(k, v)
        exp.log_parameter("status", status)
        if notes:
            exp.log_text(notes)
        exp.end()
        return
    except Exception:
        SESSION_LOG.parent.mkdir(parents=True, exist_ok=True)
        if not SESSION_LOG.exists():
            SESSION_LOG.write_text("# SESSION_LOG\n\n| timestamp | dt | status | metrics | notes |\n|---|---|---|---|---|\n")
        metrics_json = json.dumps(metrics, separators=(",", ":"))
        safe_notes = notes.replace("|", "/")
        with SESSION_LOG.open("a") as f:
            f.write(f"| {ts} | {dt_name} | {status} | `{metrics_json}` | {safe_notes} |\n")


def metric_summary(values: Iterable[float]) -> dict:
    values = np.asarray(list(values), dtype=np.float64)
    if values.size == 0:
        return {"mean": float("nan"), "p95": float("nan"), "max": float("nan")}
    return {
        "mean": float(np.mean(values)),
        "p95": float(np.percentile(values, 95)),
        "max": float(np.max(values)),
    }


def print_case(status: str, message: str) -> None:
    print(f"[{status}] {message}")


def safe_encode_decode(signal: np.ndarray, preset: str, mode: str = "balanced") -> tuple:
    # Use auto-step for DT quality checks to avoid preset step mismatch across domains.
    stream = encode(signal, preset=preset, mode=mode, step=0.0)
    reconstructed = decode(stream)
    return stream, reconstructed


def available_or_skip(ds_ids: list[str]) -> list[str]:
    available = set(list_available_datasets())
    keep = [ds for ds in ds_ids if ds in available]
    missing = [ds for ds in ds_ids if ds not in available]
    if missing:
        print_case("SKIP", f"Unavailable datasets: {', '.join(missing)}")
    return keep
