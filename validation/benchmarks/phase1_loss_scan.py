from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from validation.benchmarks._common import BENCHMARK_FIDELITY_MODE, ds_preset, zpe_metrics
from validation.datasets.loader import load_dataset
from validation.metrics.fidelity import fidelity_label, nrmse
from zpe_iot import decode, encode
from zpe_iot.presets import all_presets

DEFAULT_DATASETS = ("DS-01", "DS-05")
DEFAULT_THRESHOLDS = (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5)
AUTHORITY_BENCH = ROOT / "validation" / "results" / "bench_summary_E1_real_public_20260320T174720.json"
DEFAULT_OUTPUT = ROOT / "proofs" / "artifacts" / "LOSS_DIAGNOSIS_COMPACT.json"


def _mean(values: list[float]) -> float:
    return float(np.mean(values)) if values else 0.0


def _window_samples(samples: np.ndarray) -> np.ndarray:
    usable = (len(samples) // 256) * 256
    if usable:
        return samples[:usable].reshape(-1, 256)
    return samples.reshape(1, -1)


def _baseline_snapshot(authority_row: dict) -> dict:
    baselines = {
        "zstd": float(authority_row["zstd_cr"]),
        "lz4": float(authority_row["lz4_cr"]),
        "zlib": float(authority_row["zlib_cr"]),
        "gorilla": float(authority_row["gorilla_cr"]),
    }
    best_name = max(baselines, key=baselines.get)
    return {
        "winner": best_name,
        "best_cr": float(baselines[best_name]),
        "all": baselines,
    }


def _threshold_metrics(windows: np.ndarray, preset: str, threshold: float) -> dict:
    crs: list[float] = []
    errs: list[float] = []
    for window in windows:
        stream = encode(window, preset=preset, threshold=threshold, mode="balanced")
        packet = stream.to_bytes()
        restored = decode(packet)
        crs.append((len(window) * 8.0) / max(1, len(packet)))
        errs.append(nrmse(window, restored, mode=BENCHMARK_FIDELITY_MODE))
    return {
        "threshold": float(threshold),
        "cr": _mean(crs),
        "nrmse": _mean(errs),
    }


def _signal_stats(samples: np.ndarray, windows: np.ndarray) -> dict:
    diffs = np.diff(samples)
    unique_windows = len({row.tobytes() for row in windows})
    adjacent_repeat_windows = sum(
        1 for idx in range(len(windows) - 1) if np.array_equal(windows[idx], windows[idx + 1])
    )
    lag_256_match = (
        float(np.mean(np.isclose(samples[:-256], samples[256:]))) if len(samples) > 256 else 0.0
    )
    half_match = 0.0
    if len(samples) % 2 == 0:
        half = len(samples) // 2
        half_match = float(np.mean(np.isclose(samples[:half], samples[half:])))
    return {
        "sample_count": int(len(samples)),
        "window_count": int(len(windows)),
        "unique_ratio": float(len(np.unique(samples)) / len(samples)) if len(samples) else 0.0,
        "zero_diff_ratio": float(np.mean(np.isclose(diffs, 0.0))) if len(diffs) else 0.0,
        "diff_std": float(np.std(diffs)) if len(diffs) else 0.0,
        "sample_std": float(np.std(samples)) if len(samples) else 0.0,
        "large_jumps_gt_1std_ratio": (
            float(np.mean(np.abs(diffs) > np.std(samples))) if len(diffs) else 0.0
        ),
        "unique_windows": int(unique_windows),
        "adjacent_repeat_windows": int(adjacent_repeat_windows),
        "lag256_exact_match_ratio": lag_256_match,
        "half_match_ratio": half_match,
        "window_std_mean": float(np.mean(np.std(windows, axis=1))) if len(windows) else 0.0,
        "window_std_min": float(np.min(np.std(windows, axis=1))) if len(windows) else 0.0,
        "window_std_max": float(np.max(np.std(windows, axis=1))) if len(windows) else 0.0,
    }


def _authority_rows() -> dict[str, dict]:
    payload = json.loads(AUTHORITY_BENCH.read_text())
    return {row["dataset"]: row for row in payload["datasets"]}


def analyze_dataset(ds_id: str, authority_row: dict, thresholds: tuple[float, ...]) -> dict:
    samples = np.asarray(load_dataset(ds_id)["samples"][: 256 * 64], dtype=np.float64)
    windows = _window_samples(samples)
    mapped_preset = ds_preset(ds_id)

    mapped = zpe_metrics(samples, preset=mapped_preset, repeats=1, warmup=0)
    mapped_replay = {
        "preset": mapped_preset,
        "cr": float(mapped["cr"]),
        "nrmse": float(mapped["nrmse"]),
        "cr_diff_vs_authority": float(mapped["cr"] - float(authority_row["zpe_iot_cr"])),
        "nrmse_diff_vs_authority": float(mapped["nrmse"] - float(authority_row["zpe_iot_nrmse"])),
        "matches_authority": bool(
            abs(float(mapped["cr"]) - float(authority_row["zpe_iot_cr"])) <= 1e-6
            and abs(float(mapped["nrmse"]) - float(authority_row["zpe_iot_nrmse"])) <= 1e-9
        ),
    }

    preset_scan = []
    for preset in all_presets():
        metrics = zpe_metrics(samples, preset=preset, repeats=1, warmup=0)
        preset_scan.append(
            {
                "preset": preset,
                "cr": float(metrics["cr"]),
                "nrmse": float(metrics["nrmse"]),
                "cr_delta_vs_mapped": float(metrics["cr"] - mapped["cr"]),
                "nrmse_delta_vs_mapped": float(metrics["nrmse"] - mapped["nrmse"]),
                "nrmse_ratio_vs_mapped": (
                    float(metrics["nrmse"] / mapped["nrmse"]) if mapped["nrmse"] > 0 else None
                ),
            }
        )
    preset_scan.sort(key=lambda row: row["cr"], reverse=True)

    threshold_scan = []
    for threshold in thresholds:
        metrics = _threshold_metrics(windows, mapped_preset, threshold)
        metrics["cr_delta_vs_mapped"] = float(metrics["cr"] - mapped["cr"])
        metrics["nrmse_delta_vs_mapped"] = float(metrics["nrmse"] - mapped["nrmse"])
        metrics["nrmse_ratio_vs_mapped"] = (
            float(metrics["nrmse"] / mapped["nrmse"]) if mapped["nrmse"] > 0 else None
        )
        threshold_scan.append(metrics)

    return {
        "mapped_preset": mapped_preset,
        "authority_row": {
            "zpe_iot_cr": float(authority_row["zpe_iot_cr"]),
            "zpe_iot_nrmse": float(authority_row["zpe_iot_nrmse"]),
            "winner": authority_row["winner"],
            "baseline": _baseline_snapshot(authority_row),
        },
        "mapped_preset_replay": mapped_replay,
        "preset_scan": preset_scan,
        "threshold_scan": threshold_scan,
        "signal_stats": _signal_stats(samples, windows),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 1 DS-01 / DS-05 loss scan")
    parser.add_argument("--datasets", nargs="+", default=list(DEFAULT_DATASETS))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument(
        "--thresholds",
        nargs="+",
        type=float,
        default=list(DEFAULT_THRESHOLDS),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    authority_rows = _authority_rows()
    thresholds = tuple(float(value) for value in args.thresholds)

    results = {}
    for ds_id in args.datasets:
        if ds_id not in authority_rows:
            raise KeyError(f"Dataset {ds_id} not present in authority benchmark artifact")
        results[ds_id] = analyze_dataset(ds_id, authority_rows[ds_id], thresholds)

    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "authority_benchmark": str(AUTHORITY_BENCH.relative_to(ROOT)),
        "fidelity_metric": fidelity_label(BENCHMARK_FIDELITY_MODE),
        "window_size": 256,
        "benchmark_truncation_samples": 256 * 64,
        "thresholds": list(thresholds),
        "hardware_profile": {
            "machine": platform.machine(),
            "processor": platform.processor(),
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "datasets": results,
    }

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2))
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
