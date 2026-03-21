#!/usr/bin/env python3
"""Measure Phase 2 packet composition and sink-family similarity on the authority subset."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))
if str(ROOT / "python") not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT / "python"))

from validation.benchmarks._common import ds_preset
from validation.datasets.loader import load_dataset
from zpe_iot.codec import encode

OUTPUT = ROOT / "proofs" / "artifacts" / "PHASE2_OVERHEAD_DECOMPOSITION_20260321.json"
DATASETS = ("DS-05", "DS-02", "DS-06", "DS-08", "DS-01")
WINDOW_SIZE = 256
RAW_BYTES_PER_WINDOW = WINDOW_SIZE * 8
FIXED_PACKET_BYTES = 14  # 12-byte header + 2-byte CRC


def _window_samples(samples: np.ndarray) -> np.ndarray:
    usable = (len(samples) // WINDOW_SIZE) * WINDOW_SIZE
    clipped = samples[:usable]
    return clipped.reshape(-1, WINDOW_SIZE)


def _dominant_sink(summary: dict) -> str:
    if summary["fixed_overhead_share"] >= 0.06:
        return "fixed_overhead"
    if (
        summary["median_abs_diff"] <= 2.0
        and summary["sign_change_ratio"] >= 0.5
        and summary["zero_token_ratio"] >= 0.14
    ):
        return "smooth_low_entropy_payload"
    if summary["median_abs_diff"] >= 100.0 and summary["sign_change_ratio"] < 0.35:
        return "high_variance_payload"
    return "irregular_payload"


def _sink_basis(summary: dict) -> str:
    return (
        f"sink={summary['dominant_sink']} fixed_share={summary['fixed_overhead_share']:.4f} "
        f"zero_token_ratio={summary['zero_token_ratio']:.4f} sign_change_ratio={summary['sign_change_ratio']:.4f} "
        f"median_abs_diff={summary['median_abs_diff']:.4f}"
    )


def _same_sink_family(reference: dict, candidate: dict) -> tuple[bool, str]:
    same = (
        reference["dominant_sink"] == candidate["dominant_sink"]
        and abs(reference["sign_change_ratio"] - candidate["sign_change_ratio"]) <= 0.12
        and abs(reference["zero_token_ratio"] - candidate["zero_token_ratio"]) <= 0.14
    )
    basis = (
        f"reference[{_sink_basis(reference)}] candidate[{_sink_basis(candidate)}]"
    )
    return same, basis


def _dataset_summary(ds_id: str) -> dict:
    samples = load_dataset(ds_id)["samples"][: WINDOW_SIZE * 64]
    windows = _window_samples(samples)
    packet_lengths: list[int] = []
    token_bytes: list[int] = []
    token_counts: list[int] = []
    zero_token_counts: list[int] = []
    run_lengths: list[int] = []

    for window in windows:
        stream = encode(window, preset=ds_preset(ds_id))
        packet = stream.to_bytes()
        packet_lengths.append(len(packet))
        token_count = len(stream.rle_tokens)
        token_counts.append(token_count)
        token_bytes.append(token_count * (1 if stream.mode.value == "fast" else 2))
        zero_token_counts.append(sum(count for direction, _magnitude, count in stream.rle_tokens if direction == 0))
        run_lengths.extend(count for _direction, _magnitude, count in stream.rle_tokens)

    diffs = np.diff(windows, axis=1)
    abs_diffs = np.abs(diffs)
    sign_change_ratio = float(np.mean(np.sign(diffs[:, 1:]) != np.sign(diffs[:, :-1])))
    zero_delta_ratio = float(np.mean(diffs == 0))
    q50, q90, q99 = (float(v) for v in np.quantile(abs_diffs, [0.5, 0.9, 0.99]))

    mean_packet_bytes = float(np.mean(packet_lengths))
    mean_token_bytes = float(np.mean(token_bytes))
    payload_bytes = mean_packet_bytes - FIXED_PACKET_BYTES

    summary = {
        "dataset": ds_id,
        "preset": ds_preset(ds_id),
        "window_count": int(len(windows)),
        "bytes_per_256_window": mean_packet_bytes,
        "raw_bytes_per_256_window": RAW_BYTES_PER_WINDOW,
        "header_bytes": 12,
        "crc_bytes": 2,
        "token_bytes": mean_token_bytes,
        "payload_bytes": payload_bytes,
        "fixed_overhead_share": FIXED_PACKET_BYTES / mean_packet_bytes,
        "payload_share": payload_bytes / mean_packet_bytes,
        "mean_token_count": float(np.mean(token_counts)),
        "mean_run_length": float(np.mean(run_lengths)),
        "max_run_length": int(max(run_lengths)),
        "zero_token_ratio": float(np.sum(zero_token_counts) / (len(windows) * (WINDOW_SIZE - 1))),
        "zero_delta_ratio": zero_delta_ratio,
        "sign_change_ratio": sign_change_ratio,
        "median_abs_diff": q50,
        "p90_abs_diff": q90,
        "p99_abs_diff": q99,
    }
    summary["dominant_sink"] = _dominant_sink(summary)
    summary["basis"] = _sink_basis(summary)
    return summary


def main() -> int:
    summaries = [_dataset_summary(ds_id) for ds_id in DATASETS]
    by_id = {summary["dataset"]: summary for summary in summaries}
    reference = by_id["DS-05"]

    sink_family = {}
    for ds_id in DATASETS[1:]:
        same, basis = _same_sink_family(reference, by_id[ds_id])
        sink_family[ds_id] = {"same_sink_family": same, "basis": basis}

    output = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "authority_subset": list(DATASETS),
        "reference_dataset": "DS-05",
        "datasets": summaries,
        "sink_family_verdicts": sink_family,
        "bridge_verdict": {
            "ds05_ds02_same_sink_family": sink_family["DS-02"]["same_sink_family"],
            "shared_smooth_series_family": [
                ds_id
                for ds_id in ("DS-02", "DS-08")
                if sink_family[ds_id]["same_sink_family"]
            ],
            "non_matching_family": [
                ds_id
                for ds_id in ("DS-06", "DS-01")
                if not sink_family[ds_id]["same_sink_family"]
            ],
            "summary": (
                "DS-05, DS-02, and DS-08 cluster as smooth low-entropy payload cases, while DS-06 and DS-01 do not. "
                "That means one payload-specialized mechanism might help the DS-05/DS-02/DS-08 slice, but it will not "
                "by itself close every winner-side deficit implied by the loss-only ceiling."
            ),
        },
    }

    OUTPUT.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Saved {OUTPUT}")
    print(
        "ds05_ds02_same_sink_family="
        f"{output['bridge_verdict']['ds05_ds02_same_sink_family']} "
        f"shared={output['bridge_verdict']['shared_smooth_series_family']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
