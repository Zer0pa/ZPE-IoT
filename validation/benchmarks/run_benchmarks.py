#!/usr/bin/env python3
"""Run benchmark comparators and emit evidence-class summaries with reproducibility metadata."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.benchmarks._common import BENCHMARK_FIDELITY_MODE
from validation.metrics.fidelity import fidelity_label

RESULTS_DIR = ROOT / "validation" / "results"
MANIFEST = ROOT / "validation" / "datasets" / "manifest.json"

SCRIPTS = [
    "bench_vs_zstd.py",
    "bench_vs_lz4.py",
    "bench_vs_zlib.py",
    "bench_vs_gorilla.py",
]

CLASS_TO_EVIDENCE = {
    "proxy": "E0",
    "real_public": "E1",
    "real_customer": "E2",
}


def _latest(prefix: str) -> Path | None:
    files = sorted(RESULTS_DIR.glob(f"{prefix}_*.json"))
    return files[-1] if files else None


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _pkg_version(name: str) -> str:
    try:
        return metadata.version(name)
    except Exception:
        return "unavailable"


def _cargo_version() -> str:
    try:
        out = subprocess.check_output(["cargo", "--version"], text=True, stderr=subprocess.STDOUT).strip()
        return out
    except Exception:
        return "unavailable"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _manifest_classes() -> dict[str, str]:
    manifest = _load_json(MANIFEST)
    out: dict[str, str] = {}
    for i in range(1, 9):
        ds = f"DS-{i:02d}"
        entry = manifest.get(ds, {})
        out[ds] = str(entry.get("provenance_class", "proxy"))
    return out


def _build_rows(zstd: list[dict], lz4: list[dict], zlib: list[dict], gor: list[dict]) -> list[dict]:
    zstd_rows = {r["dataset"]: r for r in zstd}
    lz4_rows = {r["dataset"]: r for r in lz4}
    zlib_rows = {r["dataset"]: r for r in zlib}
    gor_rows = {r["dataset"]: r for r in gor}

    datasets = sorted(set(zstd_rows) & set(lz4_rows) & set(zlib_rows) & set(gor_rows))
    rows = []
    for ds in datasets:
        zpe_metric = zstd_rows[ds]["zpe_iot"]
        zstd_metric = zstd_rows[ds]["zstd"]
        lz4_metric = lz4_rows[ds]["lz4"]
        zlib_metric = zlib_rows[ds]["zlib"]
        gor_metric = gor_rows[ds]["gorilla"]

        zpe_cr = zpe_metric["cr"]

        raw_bytes = int(zpe_metric.get("raw_bytes", zstd_metric.get("raw_bytes", 0)))

        def payload_bytes(metric: dict) -> int:
            if "transport_payload_bytes" in metric:
                return int(metric["transport_payload_bytes"])
            if "compressed_bytes" in metric:
                return int(metric["compressed_bytes"])
            cr = float(metric.get("cr", 0.0))
            if raw_bytes > 0 and cr > 0.0:
                return int(round(raw_bytes / cr))
            return 0

        def reduction_pct(metric: dict) -> float:
            if "relative_reduction_vs_raw_pct" in metric:
                return float(metric["relative_reduction_vs_raw_pct"])
            payload = payload_bytes(metric)
            return ((1.0 - (payload / raw_bytes)) * 100.0) if raw_bytes else 0.0

        row = {
            "dataset": ds,
            "zpe_iot_cr": zpe_cr,
            "zpe_iot_nrmse": zpe_metric["nrmse"],
            "zpe_iot_nrmse_label": zpe_metric.get(
                "fidelity_label",
                fidelity_label(BENCHMARK_FIDELITY_MODE),
            ),
            "zstd_cr": zstd_metric["cr"],
            "lz4_cr": lz4_metric["cr"],
            "zlib_cr": zlib_metric["cr"],
            "gorilla_cr": gor_metric["cr"],
            "raw_bytes": raw_bytes,
            "zpe_transport_payload_bytes": payload_bytes(zpe_metric),
            "zstd_transport_payload_bytes": payload_bytes(zstd_metric),
            "lz4_transport_payload_bytes": payload_bytes(lz4_metric),
            "zlib_transport_payload_bytes": payload_bytes(zlib_metric),
            "gorilla_transport_payload_bytes": payload_bytes(gor_metric),
            "zpe_relative_reduction_vs_raw_pct": reduction_pct(zpe_metric),
            "zstd_relative_reduction_vs_raw_pct": reduction_pct(zstd_metric),
            "lz4_relative_reduction_vs_raw_pct": reduction_pct(lz4_metric),
            "zlib_relative_reduction_vs_raw_pct": reduction_pct(zlib_metric),
            "gorilla_relative_reduction_vs_raw_pct": reduction_pct(gor_metric),
        }
        row["winner"] = "zpe-iot" if zpe_cr > max(row["zstd_cr"], row["lz4_cr"], row["zlib_cr"], row["gorilla_cr"]) else "competitor"
        rows.append(row)
    return rows


def _summary_payload(rows: list[dict], evidence_class: str, timestamp: str, manifest_hash: str, comparator_files: dict[str, str]) -> dict:
    wins = sum(1 for r in rows if r.get("winner") == "zpe-iot")
    total = len(rows)
    pt6_pass = wins > (total / 2) if total else False
    mean_cr = float(sum(r["zpe_iot_cr"] for r in rows) / total) if total else 0.0

    if total == 0:
        pt6_status = "NOT_AVAILABLE"
        pt6_label = "NOT_AVAILABLE"
    elif evidence_class == "E0":
        pt6_status = "PASS" if pt6_pass else "FAIL"
        pt6_label = "PROVISIONAL"
    else:
        pt6_status = "PASS" if pt6_pass else "FAIL"
        pt6_label = "FINAL"

    return {
        "timestamp": timestamp,
        "evidence_class": evidence_class,
        "datasets": rows,
        "wins": wins,
        "total": total,
        "pt6_pass": pt6_pass,
        "pt6_status": pt6_status,
        "pt6_label": pt6_label,
        "mean_cr": mean_cr,
        "fidelity_metric_mode": BENCHMARK_FIDELITY_MODE.value,
        "fidelity_metric_label": fidelity_label(BENCHMARK_FIDELITY_MODE),
        "method_metadata": {
            "encode_decode_pathway": "zpe:encode_to_packet_bytes_then_decode_from_packet_bytes; baselines:compress_raw_bytes_then_decompress_raw_bytes",
            "fidelity_mode": BENCHMARK_FIDELITY_MODE.value,
            "fidelity_label": fidelity_label(BENCHMARK_FIDELITY_MODE),
            "warmup_strategy": "drop first warmup iteration from timing stats",
            "iteration_count": 5,
            "warmup_iterations": 1,
            "hardware_profile": {
                "machine": platform.machine(),
                "processor": platform.processor(),
                "platform": platform.platform(),
            },
        },
        "reproducibility": {
            "manifest_sha256": manifest_hash,
            "commands": {
                "run_benchmarks": "python validation/benchmarks/run_benchmarks.py",
                "comparators": [f"python validation/benchmarks/{name}" for name in SCRIPTS],
            },
            "toolchain": {
                "python": platform.python_version(),
                "numpy": _pkg_version("numpy"),
                "zstandard": _pkg_version("zstandard"),
                "lz4": _pkg_version("lz4"),
                "cargo": _cargo_version(),
            },
            "hardware_profile": {
                "machine": platform.machine(),
                "processor": platform.processor(),
                "platform": platform.platform(),
            },
            "inputs": comparator_files,
        },
    }


def _write(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return path


def main() -> int:
    for script in SCRIPTS:
        cmd = [sys.executable, str(Path(__file__).resolve().parent / script)]
        print(f"[RUN] {' '.join(cmd)}")
        subprocess.run(cmd, check=True, cwd=str(ROOT))

    latest = {
        "zstd": _latest("bench_vs_zstd"),
        "lz4": _latest("bench_vs_lz4"),
        "zlib": _latest("bench_vs_zlib"),
        "gorilla": _latest("bench_vs_gorilla"),
    }
    for key, path in latest.items():
        if path is None:
            raise RuntimeError(f"Missing benchmark output for {key}")

    zstd = _load_json(latest["zstd"]) ["results"]
    lz4 = _load_json(latest["lz4"]) ["results"]
    zlib = _load_json(latest["zlib"]) ["results"]
    gor = _load_json(latest["gorilla"]) ["results"]

    all_rows = _build_rows(zstd, lz4, zlib, gor)
    classes = _manifest_classes()
    for row in all_rows:
        cls = classes.get(row["dataset"], "proxy")
        row["provenance_class"] = cls
        row["evidence_class"] = CLASS_TO_EVIDENCE.get(cls, "E0")

    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    manifest_hash = _sha256(MANIFEST)
    comparator_files = {k: str(v) for k, v in latest.items()}

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    overall_evidence = "E1" if any(r["evidence_class"] in {"E1", "E2"} for r in all_rows) else "E0"
    overall = _summary_payload(all_rows, overall_evidence, ts, manifest_hash, comparator_files)
    overall_path = _write(RESULTS_DIR / f"bench_summary_{ts}.json", overall)

    split_specs = [
        ("proxy", "E0", f"bench_summary_E0_proxy_{ts}.json"),
        ("real_public", "E1", f"bench_summary_E1_real_public_{ts}.json"),
        ("real_customer", "E2", f"bench_summary_E2_real_customer_{ts}.json"),
    ]
    split_paths: dict[str, str] = {}
    for cls, evidence, fname in split_specs:
        rows = [r for r in all_rows if r.get("provenance_class") == cls]
        payload = _summary_payload(rows, evidence, ts, manifest_hash, comparator_files)
        p = _write(RESULTS_DIR / fname, payload)
        split_paths[evidence] = str(p)

    print(f"Saved summary: {overall_path}")
    print(f"PT-6 {overall['pt6_status']} ({overall['wins']}/{overall['total']} wins, {overall['pt6_label']})")
    print(f"Evidence split artifacts: {split_paths}")

    return 0 if overall["pt6_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
