#!/usr/bin/env python3
"""Probe one smooth-series payload-side mechanism on the Phase 2 authority subset."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from validation.benchmarks._common import BENCHMARK_FIDELITY_MODE, ds_preset
from validation.datasets.loader import load_dataset
from validation.metrics.fidelity import fidelity_label, nrmse
from zpe_iot import decode, encode

AUTHORITY_BENCHMARK = ROOT / "validation" / "results" / "bench_summary_E1_real_public_20260320T174720.json"
OUTPUT = ROOT / "proofs" / "artifacts" / "PHASE2_SMOOTH_SERIES_PROBE_20260321.json"

DATASETS = ("DS-05", "DS-02", "DS-08")
WINDOW_SIZE = 256
FIXED_PACKET_BYTES = 14
THRESHOLDS = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2]
FIVE_X_MEAN_TARGET = 5.0
FIVE_X_TOTAL_TARGET = FIVE_X_MEAN_TARGET * 8.0
FIDELITY_EPSILON = 1e-9

MECHANISM = {
    "id": "adaptive_threshold_gain_k_0_2",
    "description": "Increase the adaptive threshold gain from k=0.15 to k=0.2 while leaving wrappers untouched.",
    "overrides": {
        "k": 0.2,
    },
}


def _windowed(samples: np.ndarray) -> np.ndarray:
    usable = (len(samples) // WINDOW_SIZE) * WINDOW_SIZE
    clipped = samples[:usable]
    if usable == 0:
        raise RuntimeError("Need at least one full 256-sample window for the smooth-series probe")
    return clipped.reshape(-1, WINDOW_SIZE)


def _authority_rows() -> dict[str, dict]:
    payload = json.loads(AUTHORITY_BENCHMARK.read_text())
    rows = payload.get("datasets", [])
    if not rows:
        raise RuntimeError(f"No dataset rows found in {AUTHORITY_BENCHMARK}")
    return {row["dataset"]: row for row in rows}


def _evaluate_dataset(ds_id: str, overrides: dict | None = None) -> dict:
    overrides = overrides or {}
    samples = load_dataset(ds_id)["samples"][: WINDOW_SIZE * 64]
    windows = _windowed(samples)

    total_compressed_bytes = 0
    raw_total_bytes = 0
    errs: list[float] = []
    window_packet_bytes: list[int] = []
    token_counts: list[int] = []
    zero_token_counts: list[int] = []

    for window in windows:
        stream = encode(window, preset=ds_preset(ds_id), **overrides)
        packet = stream.to_bytes()
        restored = decode(packet)

        packet_bytes = len(packet)
        raw_bytes = len(window) * 8

        raw_total_bytes += raw_bytes
        total_compressed_bytes += packet_bytes
        window_packet_bytes.append(packet_bytes)
        token_counts.append(len(stream.rle_tokens))
        zero_token_counts.append(sum(count for direction, _magnitude, count in stream.rle_tokens if direction == 0))
        errs.append(nrmse(window, restored, mode=BENCHMARK_FIDELITY_MODE))

    window_count = int(len(windows))
    mean_packet_bytes = float(np.mean(window_packet_bytes))
    mean_payload_bytes = mean_packet_bytes - FIXED_PACKET_BYTES

    return {
        "dataset": ds_id,
        "preset": ds_preset(ds_id),
        "window_count": window_count,
        "raw_total_bytes": int(raw_total_bytes),
        "total_compressed_bytes": int(total_compressed_bytes),
        "bytes_per_256_window": mean_packet_bytes,
        "payload_bytes": mean_payload_bytes,
        "payload_total_bytes": int(total_compressed_bytes - (FIXED_PACKET_BYTES * window_count)),
        "fixed_packet_bytes": FIXED_PACKET_BYTES,
        "compression_ratio": float(raw_total_bytes / max(1, total_compressed_bytes)),
        "nrmse": float(np.mean(errs)),
        "mean_token_count": float(np.mean(token_counts)),
        "zero_token_ratio": float(np.sum(zero_token_counts) / max(1, window_count * (WINDOW_SIZE - 1))),
    }


def _monotonicity_probe(ds_id: str, overrides: dict) -> dict:
    samples = load_dataset(ds_id)["samples"][: WINDOW_SIZE * 64]
    windows = _windowed(samples)

    threshold_rows = []
    breaks = []

    for threshold in THRESHOLDS:
        total_compressed_bytes = 0
        raw_total_bytes = 0
        for window in windows:
            stream = encode(window, preset=ds_preset(ds_id), threshold=threshold, **overrides)
            packet = stream.to_bytes()
            raw_total_bytes += len(window) * 8
            total_compressed_bytes += len(packet)
        cr = float(raw_total_bytes / max(1, total_compressed_bytes))
        row = {
            "threshold": threshold,
            "compression_ratio": cr,
            "total_compressed_bytes": int(total_compressed_bytes),
        }
        threshold_rows.append(row)
        if len(threshold_rows) >= 2:
            previous = threshold_rows[-2]
            if row["compression_ratio"] + 1e-9 < previous["compression_ratio"]:
                breaks.append(
                    {
                        "from_threshold": previous["threshold"],
                        "to_threshold": row["threshold"],
                        "from_cr": previous["compression_ratio"],
                        "to_cr": row["compression_ratio"],
                    }
                )

    return {
        "threshold_rows": threshold_rows,
        "monotonic_breaks": breaks,
        "dt10_pass": not breaks,
    }


def _residual_budget(authority_rows: dict[str, dict], candidate_rows: dict[str, dict]) -> dict:
    projected_rows = {ds_id: float(row["zpe_iot_cr"]) for ds_id, row in authority_rows.items()}
    projected_rows.update({ds_id: row["compression_ratio"] for ds_id, row in candidate_rows.items()})

    current_total = float(sum(float(row["zpe_iot_cr"]) for row in authority_rows.values()))
    projected_total = float(sum(projected_rows.values()))
    current_mean = current_total / 8.0
    projected_mean = projected_total / 8.0

    return {
        "authority_mean_cr": current_mean,
        "projected_mean_cr_with_candidate_subset": projected_mean,
        "mean_cr_gain_from_candidate_subset": projected_mean - current_mean,
        "authority_total_cr_budget": current_total,
        "projected_total_cr_budget_with_candidate_subset": projected_total,
        "residual_total_cr_budget_to_5x": FIVE_X_TOTAL_TARGET - projected_total,
        "residual_mean_cr_to_5x": FIVE_X_MEAN_TARGET - projected_mean,
        "ds06_required_verdict": "DS-06 not yet required",
        "ds06_required_basis": (
            "This mechanism failed the fidelity guardrail, so widening to DS-06 would be premature. "
            "The measured subset still leaves a positive residual to 5.0x, but the immediate next spend "
            "should be a second smooth-series mechanism that can hold or improve benchmark NRMSE."
        ),
    }


def main() -> int:
    authority_rows = _authority_rows()

    baseline_rows = {ds_id: _evaluate_dataset(ds_id) for ds_id in DATASETS}
    candidate_rows = {ds_id: _evaluate_dataset(ds_id, MECHANISM["overrides"]) for ds_id in DATASETS}
    monotonicity = {ds_id: _monotonicity_probe(ds_id, MECHANISM["overrides"]) for ds_id in DATASETS}

    dataset_results = []
    improved_dataset_count = 0
    fidelity_guardrail_failures = []
    monotonicity_failures = []

    for ds_id in DATASETS:
        baseline = baseline_rows[ds_id]
        candidate = candidate_rows[ds_id]
        dt10 = monotonicity[ds_id]

        compression_gain = candidate["compression_ratio"] - baseline["compression_ratio"]
        compressed_byte_delta = candidate["total_compressed_bytes"] - baseline["total_compressed_bytes"]
        nrmse_delta = candidate["nrmse"] - baseline["nrmse"]
        improved = compressed_byte_delta < 0
        fidelity_guardrail_pass = nrmse_delta <= FIDELITY_EPSILON

        if improved:
            improved_dataset_count += 1
        if not fidelity_guardrail_pass:
            fidelity_guardrail_failures.append(ds_id)
        if not dt10["dt10_pass"]:
            monotonicity_failures.append(ds_id)

        dataset_results.append(
            {
                "dataset": ds_id,
                "baseline": baseline,
                "candidate": candidate,
                "delta": {
                    "compression_ratio": compression_gain,
                    "bytes_per_256_window": candidate["bytes_per_256_window"] - baseline["bytes_per_256_window"],
                    "payload_bytes": candidate["payload_bytes"] - baseline["payload_bytes"],
                    "total_compressed_bytes": compressed_byte_delta,
                    "nrmse": nrmse_delta,
                },
                "acceptance": {
                    "improved": improved,
                    "fidelity_guardrail_pass": fidelity_guardrail_pass,
                    "dt10_pass": dt10["dt10_pass"],
                },
                "monotonicity": dt10,
            }
        )

    residual_budget = _residual_budget(authority_rows, candidate_rows)
    hard_stop = bool(
        improved_dataset_count < 2
        or fidelity_guardrail_failures
        or monotonicity_failures
    )

    output = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "authority_artifact": str(AUTHORITY_BENCHMARK.relative_to(ROOT)),
        "fidelity_metric_mode": BENCHMARK_FIDELITY_MODE.value,
        "fidelity_metric_label": fidelity_label(BENCHMARK_FIDELITY_MODE),
        "mechanism": MECHANISM,
        "datasets": dataset_results,
        "subset_acceptance": {
            "improved_dataset_count": improved_dataset_count,
            "minimum_required_improvements": 2,
            "fidelity_guardrail_failures": fidelity_guardrail_failures,
            "monotonicity_failures": monotonicity_failures,
            "hard_stop": hard_stop,
        },
        "residual_budget": residual_budget,
        "verdict": {
            "retained": not hard_stop,
            "summary": (
                "The k=0.2 adaptive-threshold gain is wrapper-neutral and improves compressed bytes on DS-05, DS-02, and DS-08, "
                "but it worsens benchmark NRMSE on all three datasets. Under the current benchmark contract that is a hard stop, "
                "so the mechanism is not admissible even though DT-10 remains green on the subset."
            ),
            "next_task": (
                "Probe one more smooth-series payload-side mechanism that explicitly constrains NRMSE to stay at or below the "
                "current authority subset values before reconsidering any DS-06 spend."
            ),
        },
    }

    OUTPUT.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Saved {OUTPUT}")
    print(
        "retained="
        f"{output['verdict']['retained']} "
        f"improved={improved_dataset_count}/3 "
        f"fidelity_failures={fidelity_guardrail_failures} "
        f"dt10_failures={monotonicity_failures}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
