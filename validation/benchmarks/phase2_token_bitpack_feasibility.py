#!/usr/bin/env python3
"""Estimate the exact-fidelity upside of count-aware token bitpacking."""

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

from validation.benchmarks._common import ds_preset
from validation.datasets.loader import load_dataset
from zpe_iot import encode

AUTHORITY_BENCHMARK = ROOT / "validation" / "results" / "bench_summary_E1_real_public_20260320T174720.json"
OUTPUT = ROOT / "proofs" / "artifacts" / "PHASE2_TOKEN_BITPACK_FEASIBILITY_20260321.json"

DATASETS = tuple(f"DS-0{i}" for i in range(1, 9))
SUBSET = ("DS-05", "DS-02", "DS-08")
WINDOW_SIZE = 256
MAX_WINDOWS = 64
FIXED_PACKET_BYTES = 14
LEGACY_BALANCED_BITS = 16
COMPACT_COUNT1_BITS = 10
COMPACT_REPEAT_BITS = 17
BALANCED_MAX_COUNT = 127
FIVE_X_MEAN_TARGET = 5.0


def _windowed(samples: np.ndarray) -> np.ndarray:
    usable = min(len(samples) // WINDOW_SIZE, MAX_WINDOWS) * WINDOW_SIZE
    clipped = np.asarray(samples[:usable], dtype=np.float64)
    if usable == 0:
        raise RuntimeError("Need at least one full 256-sample window for feasibility analysis")
    return clipped.reshape(-1, WINDOW_SIZE)


def _authority_rows() -> dict[str, dict]:
    payload = json.loads(AUTHORITY_BENCHMARK.read_text())
    rows = payload.get("datasets", [])
    if not rows:
        raise RuntimeError(f"No dataset rows found in {AUTHORITY_BENCHMARK}")
    return {row["dataset"]: row for row in rows}


def _chunk_counts(count: int, limit: int) -> list[int]:
    chunks: list[int] = []
    remaining = int(count)
    while remaining > 0:
        chunk = min(remaining, limit)
        chunks.append(chunk)
        remaining -= chunk
    return chunks


def _dataset_row(ds_id: str) -> dict:
    windows = _windowed(load_dataset(ds_id)["samples"])

    raw_total_bytes = 0
    legacy_total_bytes = 0
    compact_total_bytes = 0
    chunk_count = 0
    count1_chunks = 0
    small_mag_count1_chunks = 0
    zero_direction_samples = 0

    for window in windows:
        stream = encode(window, preset=ds_preset(ds_id))
        raw_total_bytes += len(window) * 8

        legacy_payload_bits = 0
        compact_payload_bits = 0

        for direction, magnitude, count in stream.rle_tokens:
            for chunk in _chunk_counts(int(count), BALANCED_MAX_COUNT):
                chunk_count += 1
                legacy_payload_bits += LEGACY_BALANCED_BITS
                if chunk == 1:
                    count1_chunks += 1
                    compact_payload_bits += COMPACT_COUNT1_BITS
                    if direction != 0 and magnitude <= 3:
                        small_mag_count1_chunks += 1
                else:
                    compact_payload_bits += COMPACT_REPEAT_BITS
                if direction == 0:
                    zero_direction_samples += chunk

        legacy_total_bytes += FIXED_PACKET_BYTES + (legacy_payload_bits // 8)
        compact_total_bytes += FIXED_PACKET_BYTES + ((compact_payload_bits + 7) // 8)

    sample_transitions = max(1, len(windows) * (WINDOW_SIZE - 1))
    count1_share = count1_chunks / max(1, chunk_count)

    return {
        "dataset": ds_id,
        "preset": ds_preset(ds_id),
        "window_count": int(len(windows)),
        "raw_total_bytes": int(raw_total_bytes),
        "legacy_total_bytes": int(legacy_total_bytes),
        "compact_total_bytes": int(compact_total_bytes),
        "legacy_compression_ratio": float(raw_total_bytes / max(1, legacy_total_bytes)),
        "compact_compression_ratio_estimate": float(raw_total_bytes / max(1, compact_total_bytes)),
        "compression_ratio_gain_estimate": float((raw_total_bytes / max(1, compact_total_bytes)) - (raw_total_bytes / max(1, legacy_total_bytes))),
        "chunk_token_count": int(chunk_count),
        "count1_chunk_share": float(count1_share),
        "small_magnitude_count1_share": float(small_mag_count1_chunks / max(1, chunk_count)),
        "zero_direction_sample_share": float(zero_direction_samples / sample_transitions),
        "legacy_payload_bytes_per_window": float((legacy_total_bytes / len(windows)) - FIXED_PACKET_BYTES),
        "compact_payload_bytes_per_window_estimate": float((compact_total_bytes / len(windows)) - FIXED_PACKET_BYTES),
        "fixed_packet_bytes_per_window": FIXED_PACKET_BYTES,
    }


def _authority_projection(authority_rows: dict[str, dict], measured_rows: dict[str, dict], active_datasets: tuple[str, ...]) -> dict:
    projected_rows = {ds_id: float(row["zpe_iot_cr"]) for ds_id, row in authority_rows.items()}
    for ds_id in active_datasets:
        projected_rows[ds_id] = measured_rows[ds_id]["compact_compression_ratio_estimate"]

    authority_total = float(sum(float(row["zpe_iot_cr"]) for row in authority_rows.values()))
    projected_total = float(sum(projected_rows.values()))
    authority_mean = authority_total / len(authority_rows)
    projected_mean = projected_total / len(authority_rows)

    return {
        "active_datasets": list(active_datasets),
        "authority_mean_cr": authority_mean,
        "projected_mean_cr": projected_mean,
        "projected_mean_gain": projected_mean - authority_mean,
        "authority_total_cr_budget": authority_total,
        "projected_total_cr_budget": projected_total,
        "residual_mean_cr_to_5x": FIVE_X_MEAN_TARGET - projected_mean,
    }


def main() -> int:
    authority_rows = _authority_rows()
    measured_rows = {ds_id: _dataset_row(ds_id) for ds_id in DATASETS}

    subset_mean_gain = float(np.mean([measured_rows[ds_id]["compression_ratio_gain_estimate"] for ds_id in SUBSET]))
    subset_projection = _authority_projection(authority_rows, measured_rows, SUBSET)
    all_projection = _authority_projection(authority_rows, measured_rows, DATASETS)

    output = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "authority_artifact": str(AUTHORITY_BENCHMARK.relative_to(ROOT)),
        "mechanism": {
            "id": "count_aware_exact_fidelity_token_bitpack",
            "description": (
                "Use the reserved packet flag bit to switch balanced and lossless streams to a count-aware bitstream: "
                "10 bits for count==1 tokens and 17 bits for repeated tokens, leaving quantisation and decode fidelity unchanged."
            ),
            "legacy_bits_per_chunk": LEGACY_BALANCED_BITS,
            "compact_bits_per_count1_chunk": COMPACT_COUNT1_BITS,
            "compact_bits_per_repeat_chunk": COMPACT_REPEAT_BITS,
        },
        "datasets": [measured_rows[ds_id] for ds_id in DATASETS],
        "subset_projection_from_authority": subset_projection,
        "full_projection_from_authority": all_projection,
        "bridge_signal": {
            "subset": list(SUBSET),
            "subset_mean_gain_estimate": subset_mean_gain,
            "count1_share_floor_on_subset": float(min(measured_rows[ds_id]["count1_chunk_share"] for ds_id in SUBSET)),
            "count1_share_floor_all_e1": float(min(row["count1_chunk_share"] for row in measured_rows.values())),
            "verdict": (
                "The smooth-series subset still exposes a stronger structural signal than threshold tuning: count==1 token dominance. "
                "Because the candidate mechanism only changes packet representation, not quantisation, it preserves exact decode fidelity in principle "
                "and is large enough in estimate to justify one bounded implementation attempt before Phase 2 is downgraded."
            ),
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
