#!/usr/bin/env python3
"""Freeze Phase 2 authority-gap math from the March 20 E1 benchmark artifact."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = ROOT / "validation" / "results" / "bench_summary_E1_real_public_20260320T174720.json"
OUTPUT = ROOT / "proofs" / "artifacts" / "PHASE2_GAP_BUDGET_20260321.json"

LOSS_SET = {"DS-01", "DS-05"}
WINNING_BRIDGE_SET = ("DS-02", "DS-06", "DS-08")


def _load_rows() -> list[dict]:
    payload = json.loads(BENCHMARK.read_text())
    rows = payload.get("datasets", [])
    if not rows:
        raise RuntimeError(f"No dataset rows found in {BENCHMARK}")
    return rows


def _best_baseline(row: dict) -> float:
    return max(float(row["zstd_cr"]), float(row["lz4_cr"]), float(row["zlib_cr"]), float(row["gorilla_cr"]))


def _dataset_summary(row: dict) -> dict:
    current_cr = float(row["zpe_iot_cr"])
    best_baseline_cr = _best_baseline(row)
    comparator_headroom = max(0.0, best_baseline_cr - current_cr)
    gap_to_five_x = max(0.0, 5.0 - current_cr)
    return {
        "dataset": row["dataset"],
        "winner": row["winner"],
        "current_cr": current_cr,
        "best_baseline_cr": best_baseline_cr,
        "comparator_headroom": comparator_headroom,
        "gap_to_5x": gap_to_five_x,
        "raw_bytes": int(row["raw_bytes"]),
        "zpe_payload_bytes": int(row["zpe_transport_payload_bytes"]),
    }


def main() -> int:
    rows = _load_rows()
    datasets = [_dataset_summary(row) for row in rows]
    by_id = {row["dataset"]: row for row in datasets}

    current_total = sum(row["current_cr"] for row in datasets)
    target_total = 5.0 * len(datasets)
    missing_total = target_total - current_total

    loss_only_total = current_total + sum(by_id[ds]["comparator_headroom"] for ds in LOSS_SET)
    loss_only_mean = loss_only_total / len(datasets)
    residual_after_loss_only = target_total - loss_only_total

    winning_gap_sum = sum(by_id[ds]["gap_to_5x"] for ds in WINNING_BRIDGE_SET)
    triad_total_if_reaches_5x = loss_only_total + winning_gap_sum
    triad_mean_if_reaches_5x = triad_total_if_reaches_5x / len(datasets)

    single_bridge_candidates = [
        row["dataset"]
        for row in datasets
        if row["dataset"] not in LOSS_SET and row["gap_to_5x"] >= residual_after_loss_only
    ]

    ranked_by_target_gap = sorted(
        (row for row in datasets if row["dataset"] not in LOSS_SET),
        key=lambda row: row["gap_to_5x"],
        reverse=True,
    )
    ranked_by_comparator_headroom = sorted(datasets, key=lambda row: row["comparator_headroom"], reverse=True)

    output = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "authority_artifact": str(BENCHMARK.relative_to(ROOT)),
        "current_mean_cr": current_total / len(datasets),
        "current_total_cr_budget": current_total,
        "target_mean_cr": 5.0,
        "target_total_cr_budget": target_total,
        "missing_total_cr_budget": missing_total,
        "loss_only_ceiling": {
            "datasets": sorted(LOSS_SET),
            "ceiling_total_cr_budget": loss_only_total,
            "ceiling_mean_cr": loss_only_mean,
            "residual_after_loss_only": residual_after_loss_only,
        },
        "bridge_analysis": {
            "ranked_by_gap_to_5x": ranked_by_target_gap,
            "ranked_by_comparator_headroom": ranked_by_comparator_headroom,
            "single_bridge_dataset": single_bridge_candidates[0] if single_bridge_candidates else None,
            "single_bridge_dataset_supported": bool(single_bridge_candidates),
            "winning_bridge_set": list(WINNING_BRIDGE_SET),
            "winning_bridge_gap_to_5x_total": winning_gap_sum,
            "triad_total_if_bridge_set_reaches_5x": triad_total_if_reaches_5x,
            "triad_mean_if_bridge_set_reaches_5x": triad_mean_if_reaches_5x,
        },
        "verdict": {
            "ds02_comparator_bridge_supported": False,
            "summary": (
                "The March 20 E1 authority artifact does not support DS-02 as a single comparator-headroom bridge dataset. "
                "DS-02 already beats the baselines on this surface, so the bridge problem must be framed as additional gap-to-5x "
                "recovery across multiple winners, not as DS-02 alone repaying the residual budget."
            ),
            "next_bridge_focus": ["DS-05", "DS-02", "DS-08", "DS-06"],
        },
    }

    OUTPUT.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Saved {OUTPUT}")
    print(
        "loss_only_mean="
        f"{loss_only_mean:.6f} residual_after_loss_only={residual_after_loss_only:.6f} "
        f"single_bridge_dataset={output['bridge_analysis']['single_bridge_dataset']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
