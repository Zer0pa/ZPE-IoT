#!/usr/bin/env python3
"""Emit dataset-level public benchmark receipts from the latest E1 surface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import lz4.frame
import numpy as np
import zlib
import zstandard as zstd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))
if str(ROOT / "python") not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT / "python"))

from validation.benchmarks._common import benchmark_dataset, ds_preset
from validation.datasets.loader import iter_dataset_windows, load_dataset
from zpe_iot import decode, encode

RESULTS_DIR = ROOT / "validation" / "results"
MANIFEST = ROOT / "validation" / "datasets" / "manifest.json"
OUTPUT_DIR = ROOT / "proofs" / "artifacts" / "public_benchmarks"
PHASE8_PROOF = ROOT / "proofs" / "artifacts" / "PHASE8_DATASET_EXPANSION_20260321.md"
PHASE9_PROOF = ROOT / "proofs" / "artifacts" / "PHASE9_BENCHMARK_OBSERVABILITY_20260321.md"


def _latest(prefix: str) -> Path | None:
    files = sorted(RESULTS_DIR.glob(f"{prefix}_*.json"))
    return files[-1] if files else None


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _ds_sort_key(ds_id: str) -> int:
    return int(ds_id.split("-")[1])


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _parity_summary(ds_id: str, max_windows: int = 8) -> dict:
    preset = ds_preset(ds_id)
    checked = 0
    failures: list[int] = []
    for idx, window in enumerate(iter_dataset_windows(ds_id)):
        packet = encode(window, preset=preset).to_bytes()
        restored = np.asarray(decode(packet), dtype=np.float64)
        replay = encode(restored, preset=preset).to_bytes()
        checked += 1
        if replay != packet:
            failures.append(idx)
        if checked >= max_windows:
            break
    return {
        "checked_windows": checked,
        "packet_roundtrip_bit_parity": len(failures) == 0,
        "failure_windows": failures[:3],
        "definition": "encode(window) bytes must equal encode(decode(packet)) bytes on sampled windows",
    }


def _validate_committed_receipts(summary_path: Path) -> int:
    index_path = OUTPUT_DIR / "INDEX.json"
    if not index_path.exists():
        raise FileNotFoundError(f"Committed benchmark index missing: {index_path}")

    summary = _load(summary_path)
    index = _load(index_path)

    if summary.get("evidence_class") != "E1":
        raise ValueError("Expected E1 benchmark summary")
    if index.get("evidence_class") != summary.get("evidence_class"):
        raise ValueError("Committed benchmark index evidence class drifted from summary")
    if int(summary.get("wins", -1)) != 10 or int(summary.get("total", -1)) != 11:
        raise ValueError("Committed benchmark summary no longer matches 10/11 E1 surface")

    blocked = {row["dataset"]: row for row in index.get("blocked_datasets", [])}
    if "DS-11" not in blocked or blocked["DS-11"].get("status") != "BLOCKED":
        raise ValueError("DS-11 blocked disclosure missing from committed benchmark index")

    receipts = {row["dataset"]: row for row in index.get("datasets", [])}
    if "DS-12" not in receipts or receipts["DS-12"].get("winner") != "competitor":
        raise ValueError("DS-12 competitor disclosure missing from committed benchmark receipts")

    for ds_id, row in receipts.items():
        artifact_path = ROOT / row["artifact"]
        if not artifact_path.exists():
            raise FileNotFoundError(f"Committed benchmark receipt missing: {artifact_path}")
        payload = _load(artifact_path)
        if payload.get("dataset") != ds_id:
            raise ValueError(f"Receipt dataset mismatch for {ds_id}")
        if payload.get("status") != row.get("status"):
            raise ValueError(f"Receipt status mismatch for {ds_id}")
        if row.get("status") != "BLOCKED" and payload.get("winner") != row.get("winner"):
            raise ValueError(f"Receipt winner mismatch for {ds_id}")

    print(
        "Validated committed public benchmark receipts "
        f"({len(receipts)} receipts, wins={summary['wins']}/{summary['total']}, DS-12 competitor disclosure present)"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--datasets",
        nargs="*",
        default=None,
        help="Optional dataset IDs to export. Datasets outside the latest E1 summary are benchmarked on demand.",
    )
    args = parser.parse_args()

    manifest = _load(MANIFEST)
    summary_path = _latest("bench_summary_E1_real_public")
    if summary_path is None:
        raise FileNotFoundError("No benchmark artifact found for bench_summary_E1_real_public")

    tracking_path = _latest("benchmark_tracking_context")
    zstd_path = _latest("bench_vs_zstd")
    lz4_path = _latest("bench_vs_lz4")
    zlib_path = _latest("bench_vs_zlib")
    gorilla_path = _latest("bench_vs_gorilla")

    if None in {tracking_path, zstd_path, lz4_path, zlib_path, gorilla_path}:
        return _validate_committed_receipts(summary_path)

    summary = _load(summary_path)
    tracking_context = _load(tracking_path)

    zstd_rows = {row["dataset"]: row for row in _load(zstd_path)["results"]}
    lz4_rows = {row["dataset"]: row for row in _load(lz4_path)["results"]}
    zlib_rows = {row["dataset"]: row for row in _load(zlib_path)["results"]}
    gorilla_rows = {row["dataset"]: row for row in _load(gorilla_path)["results"]}
    summary_rows = {row["dataset"]: row for row in summary["datasets"]}

    ready_ids = sorted(
        (ds_id for ds_id, entry in manifest.items() if entry.get("status") == "READY"),
        key=_ds_sort_key,
    )
    blocked_rows = [
        {
            "dataset": ds_id,
            "name": entry.get("name", ds_id),
            "status": entry.get("status", "UNKNOWN"),
            "provenance_class": entry.get("provenance_class"),
            "source_url": entry.get("source_url"),
            "license": entry.get("license"),
            "notes": entry.get("notes", ""),
            "blocked_reason": entry.get("blocked_reason", ""),
        }
        for ds_id, entry in sorted(manifest.items(), key=lambda item: _ds_sort_key(item[0]))
        if entry.get("status") != "READY"
    ]
    requested = args.datasets or sorted(
        set(summary_rows) | {row["dataset"] for row in blocked_rows},
        key=_ds_sort_key,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    index_rows: list[dict] = []

    def _gorilla_proxy(raw: bytes) -> bytes:
        arr = np.frombuffer(raw, dtype=np.float64)
        bits = arr.view(np.uint64).copy()
        count = int(len(bits))
        if count == 0:
            return (0).to_bytes(4, "little")
        if count == 1:
            return (1).to_bytes(4, "little") + bits[:1].tobytes()
        xor = np.bitwise_xor(bits[1:], bits[:-1])
        return count.to_bytes(4, "little") + bits[:1].tobytes() + zlib.compress(xor.tobytes(), level=6)

    def _gorilla_proxy_decompress(blob: bytes) -> bytes:
        if len(blob) < 4:
            raise ValueError("gorilla blob too short")
        count = int.from_bytes(blob[:4], "little")
        if count == 0:
            return b""
        if len(blob) < 12:
            raise ValueError("gorilla blob missing seed value")
        seed = np.frombuffer(blob[4:12], dtype=np.uint64).copy()
        if count == 1:
            return seed.view(np.float64).tobytes()
        xor = np.frombuffer(zlib.decompress(blob[12:]), dtype=np.uint64)
        out = np.empty(count, dtype=np.uint64)
        out[0] = seed[0]
        for idx in range(1, count):
            out[idx] = out[idx - 1] ^ xor[idx - 1]
        return out.view(np.float64).tobytes()

    def _ensure_dataset_rows(ds_id: str) -> tuple[dict, dict, dict, dict, dict]:
        if ds_id in summary_rows:
            return (
                summary_rows[ds_id],
                zstd_rows[ds_id],
                lz4_rows[ds_id],
                zlib_rows[ds_id],
                gorilla_rows[ds_id],
            )

        zstd_comp = zstd.ZstdCompressor(level=3)
        zstd_decomp = zstd.ZstdDecompressor()
        zstd_row = benchmark_dataset(
            ds_id,
            "zstd",
            zstd_comp.compress,
            zstd_decomp.decompress,
            repeats=5,
            warmup=1,
        )
        lz4_row = benchmark_dataset(
            ds_id,
            "lz4",
            lz4.frame.compress,
            lz4.frame.decompress,
            repeats=5,
            warmup=1,
        )
        zlib_row = benchmark_dataset(
            ds_id,
            "zlib",
            lambda payload: zlib.compress(payload, level=6),
            zlib.decompress,
            repeats=5,
            warmup=1,
        )
        gorilla_row = benchmark_dataset(
            ds_id,
            "gorilla",
            _gorilla_proxy,
            _gorilla_proxy_decompress,
            repeats=5,
            warmup=1,
        )
        summary_row = {
            "dataset": ds_id,
            "zpe_iot_cr": zstd_row["zpe_iot"]["cr"],
            "zpe_iot_nrmse": zstd_row["zpe_iot"]["nrmse"],
            "zstd_cr": zstd_row["zstd"]["cr"],
            "lz4_cr": lz4_row["lz4"]["cr"],
            "zlib_cr": zlib_row["zlib"]["cr"],
            "gorilla_cr": gorilla_row["gorilla"]["cr"],
            "winner": zstd_row["winner"],
        }
        return summary_row, zstd_row, lz4_row, zlib_row, gorilla_row

    for ds_id in requested:
        manifest_entry = manifest[ds_id]
        status = str(manifest_entry.get("status", "READY")).upper()
        if status == "BLOCKED":
            payload = {
                "dataset": ds_id,
                "name": manifest_entry.get("name", ds_id),
                "status": status,
                "evidence_class": summary["evidence_class"],
                "source": {
                    "source_url": manifest_entry.get("source_url"),
                    "license": manifest_entry.get("license"),
                    "blocked_reason": manifest_entry.get("blocked_reason", ""),
                    "notes": manifest_entry.get("notes", ""),
                },
                "observability": tracking_context.get("tracking", {}),
                "source_artifacts": {
                    "manifest": _relative(MANIFEST),
                    "summary": _relative(summary_path),
                    "tracking": _relative(tracking_path),
                    "phase8_proof": _relative(PHASE8_PROOF),
                    "phase9_proof": _relative(PHASE9_PROOF),
                },
            }
            winner = "blocked"
            compression_ratio = None
        else:
            row, zstd_row, lz4_row, zlib_row, gorilla_row = _ensure_dataset_rows(ds_id)
            dataset = load_dataset(ds_id)
            parity = _parity_summary(ds_id)
            payload = {
                "dataset": ds_id,
                "name": dataset["name"],
                "status": status,
                "evidence_class": summary["evidence_class"],
                "preset": ds_preset(ds_id),
                "source": {
                    "source_url": manifest_entry.get("source_url"),
                    "license": manifest_entry.get("license"),
                    "raw_sha256": manifest_entry.get("raw_sha256"),
                    "transform_sha256": manifest_entry.get("transform_sha256"),
                },
                "zpe_iot": {
                    "compression_ratio": row["zpe_iot_cr"],
                    "encode_latency_us": round(float(zstd_row["zpe_iot"]["encode_ms"]) * 1000.0, 3),
                    "decode_latency_us": round(float(zstd_row["zpe_iot"]["decode_ms"]) * 1000.0, 3),
                    "nrmse": row["zpe_iot_nrmse"],
                },
                "comparators": {
                    "zstd_cr": row["zstd_cr"],
                    "lz4_cr": row["lz4_cr"],
                    "zlib_cr": row["zlib_cr"],
                    "gorilla_cr": row["gorilla_cr"],
                },
                "winner": row["winner"],
                "roundtrip": parity,
                "observability": tracking_context.get("tracking", {}),
                "source_artifacts": {
                    "manifest": _relative(MANIFEST),
                    "summary": _relative(summary_path),
                    "tracking": _relative(tracking_path),
                    "zstd": _relative(zstd_path),
                    "lz4": _relative(lz4_path),
                    "zlib": _relative(zlib_path),
                    "gorilla": _relative(gorilla_path),
                    "phase8_proof": _relative(PHASE8_PROOF),
                    "phase9_proof": _relative(PHASE9_PROOF),
                },
            }
            winner = row["winner"]
            compression_ratio = row["zpe_iot_cr"]
        out_path = OUTPUT_DIR / f"{ds_id}.json"
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        index_rows.append(
            {
                "dataset": ds_id,
                "name": manifest_entry.get("name", ds_id),
                "status": status,
                "winner": winner,
                "compression_ratio": compression_ratio,
                "artifact": _relative(out_path),
            }
        )

    tracking = tracking_context.get("tracking", {})
    index_payload = {
        "evidence_class": summary["evidence_class"],
        "benchmark_boundary": "11 READY + 1 BLOCKED",
        "surface": {
            "ready_dataset_count": len(ready_ids),
            "blocked_dataset_count": len(blocked_rows),
            "benchmark_executable_dataset_count": len(summary_rows),
            "exported_receipt_count": len(index_rows),
        },
        "requested_datasets": requested,
        "wins": summary["wins"],
        "total": summary["total"],
        "mean_cr": summary["mean_cr"],
        "blocked_datasets": blocked_rows,
        "datasets": index_rows,
        "observability": {
            "workspace": tracking.get("workspace"),
            "classic_project": tracking.get("classic_project"),
            "classic_status": tracking.get("classic_status"),
            "classic_handshake_error": tracking_context.get("classic_check", {}).get("handshake_error", ""),
            "opik_project": tracking.get("opik_project"),
            "opik_status": tracking.get("opik_status"),
            "opik_handshake_error": tracking_context.get("opik_check", {}).get("handshake_error", ""),
            "opik_host": tracking.get("opik_host"),
            "notes": tracking.get("notes", []),
        },
        "source_artifacts": {
            "manifest": _relative(MANIFEST),
            "summary": _relative(summary_path),
            "tracking": _relative(tracking_path),
            "zstd": _relative(zstd_path),
            "lz4": _relative(lz4_path),
            "zlib": _relative(zlib_path),
            "gorilla": _relative(gorilla_path),
            "phase8_proof": _relative(PHASE8_PROOF),
            "phase9_proof": _relative(PHASE9_PROOF),
        },
    }
    (OUTPUT_DIR / "INDEX.json").write_text(json.dumps(index_payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
