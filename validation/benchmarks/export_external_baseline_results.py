#!/usr/bin/env python3
"""Export external baseline results with payload-economics framing."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "validation" / "results"


def _latest_summary() -> Path:
    files = sorted(RESULTS_DIR.glob("bench_summary_[0-9]*.json"))
    if not files:
        raise FileNotFoundError("No bench_summary artifacts found")
    return files[-1]


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _mean(values: list[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def build_payload(summary: dict, summary_path: Path) -> dict:
    datasets = summary.get("datasets", [])
    payload_rows: list[dict] = []

    for row in datasets:
        payload_rows.append(
            {
                "dataset": row["dataset"],
                "raw_bytes": int(row.get("raw_bytes", 0)),
                "payload_economics": [
                    {
                        "compressor": "zpe",
                        "transport_payload_bytes": int(row.get("zpe_transport_payload_bytes", 0)),
                        "relative_reduction_vs_raw_pct": float(row.get("zpe_relative_reduction_vs_raw_pct", 0.0)),
                        "compression_ratio": float(row.get("zpe_iot_cr", 0.0)),
                    },
                    {
                        "compressor": "zstd",
                        "transport_payload_bytes": int(row.get("zstd_transport_payload_bytes", 0)),
                        "relative_reduction_vs_raw_pct": float(row.get("zstd_relative_reduction_vs_raw_pct", 0.0)),
                        "compression_ratio": float(row.get("zstd_cr", 0.0)),
                    },
                    {
                        "compressor": "lz4",
                        "transport_payload_bytes": int(row.get("lz4_transport_payload_bytes", 0)),
                        "relative_reduction_vs_raw_pct": float(row.get("lz4_relative_reduction_vs_raw_pct", 0.0)),
                        "compression_ratio": float(row.get("lz4_cr", 0.0)),
                    },
                    {
                        "compressor": "zlib",
                        "transport_payload_bytes": int(row.get("zlib_transport_payload_bytes", 0)),
                        "relative_reduction_vs_raw_pct": float(row.get("zlib_relative_reduction_vs_raw_pct", 0.0)),
                        "compression_ratio": float(row.get("zlib_cr", 0.0)),
                    },
                    {
                        "compressor": "gorilla",
                        "transport_payload_bytes": int(row.get("gorilla_transport_payload_bytes", 0)),
                        "relative_reduction_vs_raw_pct": float(row.get("gorilla_relative_reduction_vs_raw_pct", 0.0)),
                        "compression_ratio": float(row.get("gorilla_cr", 0.0)),
                    },
                ],
            }
        )

    def collect(compressor: str, key: str) -> list[float]:
        out: list[float] = []
        for ds in payload_rows:
            for entry in ds["payload_economics"]:
                if entry["compressor"] == compressor:
                    out.append(float(entry[key]))
        return out

    aggregate = {}
    for comp in ["zpe", "zstd", "lz4", "zlib", "gorilla"]:
        aggregate[comp] = {
            "mean_transport_payload_bytes": _mean(collect(comp, "transport_payload_bytes")),
            "mean_relative_reduction_vs_raw_pct": _mean(collect(comp, "relative_reduction_vs_raw_pct")),
            "mean_compression_ratio": _mean(collect(comp, "compression_ratio")),
        }

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_summary_artifact": str(summary_path),
        "comparator_contract": ["zpe", "zlib", "lz4", "zstd", "gorilla"],
        "payload_economics_contract": {
            "includes_transport_payload_bytes": True,
            "includes_relative_reduction_vs_raw": True,
            "includes_packet_framing_for_zpe": True,
        },
        "method_metadata": summary.get("method_metadata", {}),
        "datasets": payload_rows,
        "aggregate": aggregate,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=None, help="Optional bench_summary_*.json path")
    parser.add_argument("--out", type=Path, required=True, help="Output artifact path")
    args = parser.parse_args()

    summary_path = args.summary if args.summary else _latest_summary()
    summary = _load(summary_path)
    payload = build_payload(summary, summary_path)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Saved: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
