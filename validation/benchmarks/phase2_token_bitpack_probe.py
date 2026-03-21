#!/usr/bin/env python3
"""Measure the Phase 2 exact-fidelity token-bitpack line."""

from __future__ import annotations

import json
import os
import subprocess
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
from zpe_iot import Config, decode, encode
from zpe_iot import _native
from zpe_iot.codec import pack_stream

AUTHORITY_BENCHMARK = ROOT / "validation" / "results" / "bench_summary_E1_real_public_20260320T174720.json"
OUTPUT = ROOT / "proofs" / "artifacts" / "PHASE2_TOKEN_BITPACK_PROBE_20260321.json"
RUN_BENCHMARKS = ROOT / "validation" / "benchmarks" / "run_benchmarks.py"

DATASETS = ("DS-05", "DS-02", "DS-08")
WINDOW_SIZE = 256
MAX_WINDOWS = 64
THRESHOLDS = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]
FIDELITY_EPSILON = 1e-12


def _windowed(samples: np.ndarray) -> np.ndarray:
    usable = min(len(samples) // WINDOW_SIZE, MAX_WINDOWS) * WINDOW_SIZE
    clipped = np.asarray(samples[:usable], dtype=np.float64)
    if usable == 0:
        raise RuntimeError("Need at least one full 256-sample window for the token-bitpack probe")
    return clipped.reshape(-1, WINDOW_SIZE)


def _authority_rows() -> dict[str, dict]:
    payload = json.loads(AUTHORITY_BENCHMARK.read_text())
    rows = payload.get("datasets", [])
    if not rows:
        raise RuntimeError(f"No dataset rows found in {AUTHORITY_BENCHMARK}")
    return {row["dataset"]: row for row in rows}


def _latest(prefix: str) -> Path | None:
    files = sorted((ROOT / "validation" / "results").glob(f"{prefix}_*.json"))
    return files[-1] if files else None


def _subset_row(ds_id: str) -> dict:
    windows = _windowed(load_dataset(ds_id)["samples"])

    raw_total_bytes = 0
    legacy_total_bytes = 0
    candidate_total_bytes = 0
    legacy_errs: list[float] = []
    candidate_errs: list[float] = []
    decode_match = True

    for window in windows:
        stream = encode(window, preset=ds_preset(ds_id))
        legacy_packet = pack_stream(stream, compact=False)
        candidate_packet = stream.to_bytes()

        legacy_restored = decode(legacy_packet)
        candidate_restored = decode(candidate_packet)

        raw_total_bytes += len(window) * 8
        legacy_total_bytes += len(legacy_packet)
        candidate_total_bytes += len(candidate_packet)
        legacy_errs.append(nrmse(window, legacy_restored, mode=BENCHMARK_FIDELITY_MODE))
        candidate_errs.append(nrmse(window, candidate_restored, mode=BENCHMARK_FIDELITY_MODE))
        decode_match = decode_match and np.allclose(legacy_restored, candidate_restored, rtol=0.0, atol=1e-12)

    legacy_cr = float(raw_total_bytes / max(1, legacy_total_bytes))
    candidate_cr = float(raw_total_bytes / max(1, candidate_total_bytes))
    legacy_nrmse = float(np.mean(legacy_errs))
    candidate_nrmse = float(np.mean(candidate_errs))

    return {
        "dataset": ds_id,
        "preset": ds_preset(ds_id),
        "window_count": int(len(windows)),
        "legacy_compression_ratio": legacy_cr,
        "candidate_compression_ratio": candidate_cr,
        "compression_ratio_gain": candidate_cr - legacy_cr,
        "legacy_total_bytes": int(legacy_total_bytes),
        "candidate_total_bytes": int(candidate_total_bytes),
        "compressed_byte_delta": int(candidate_total_bytes - legacy_total_bytes),
        "legacy_nrmse": legacy_nrmse,
        "candidate_nrmse": candidate_nrmse,
        "nrmse_delta": candidate_nrmse - legacy_nrmse,
        "decode_match": decode_match,
        "acceptance": {
            "improved": candidate_total_bytes < legacy_total_bytes,
            "fidelity_guardrail_pass": (candidate_nrmse - legacy_nrmse) <= FIDELITY_EPSILON,
            "decode_match": decode_match,
        },
    }


def _dt10_row() -> dict:
    samples = load_dataset("DS-02")["samples"][:20_480]
    rows = []
    for threshold in THRESHOLDS:
        stream = encode(samples, preset="vibration", threshold=threshold, mode="balanced")
        rows.append(
            {
                "threshold": threshold,
                "compression_ratio": stream.compression_ratio,
                "packet_bytes": stream.packed_size,
            }
        )
    passes = all(rows[i]["compression_ratio"] <= rows[i + 1]["compression_ratio"] + 1e-9 for i in range(len(rows) - 1))
    return {
        "threshold_rows": rows,
        "dt10_pass": passes,
    }


def _dt11_row() -> dict:
    if not _native.available():
        return {
            "dt11_pass": False,
            "native_available": False,
            "mismatch_index": None,
        }

    rng = np.random.default_rng(123)
    cfg = Config.from_preset("vibration")
    mismatch_index = None
    for idx in range(100):
        x = rng.standard_normal(256)
        py_packet = encode(x, config=cfg).to_bytes()
        rs_packet = _native.encode(x, config=cfg)
        if py_packet != rs_packet:
            mismatch_index = idx
            break

    return {
        "dt11_pass": mismatch_index is None,
        "native_available": True,
        "mismatch_index": mismatch_index,
    }


def _run_authority_benchmark(env: dict[str, str]) -> dict:
    before = set((ROOT / "validation" / "results").glob("bench_summary_E1_real_public_*.json"))
    completed = subprocess.run(
        [sys.executable, str(RUN_BENCHMARKS)],
        cwd=str(ROOT),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    after = set((ROOT / "validation" / "results").glob("bench_summary_E1_real_public_*.json"))
    created = sorted(after - before)
    latest = created[-1] if created else _latest("bench_summary_E1_real_public")

    result = {
        "command": f"{sys.executable} {RUN_BENCHMARKS.relative_to(ROOT)}",
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout.strip().splitlines()[-10:],
        "stderr_tail": completed.stderr.strip().splitlines()[-10:],
        "artifact": str(latest.relative_to(ROOT)) if latest else None,
    }
    if latest and latest.exists():
        payload = json.loads(latest.read_text())
        result["mean_cr"] = float(payload.get("mean_cr", 0.0))
        result["wins"] = int(payload.get("wins", 0))
        result["total"] = int(payload.get("total", 0))
    return result


def main() -> int:
    authority_rows = _authority_rows()
    subset_results = [_subset_row(ds_id) for ds_id in DATASETS]
    improved_count = sum(1 for row in subset_results if row["acceptance"]["improved"])
    fidelity_failures = [row["dataset"] for row in subset_results if not row["acceptance"]["fidelity_guardrail_pass"]]
    decode_failures = [row["dataset"] for row in subset_results if not row["acceptance"]["decode_match"]]

    dt10 = _dt10_row()
    dt11 = _dt11_row()

    subset_pass = (
        improved_count >= 2
        and not fidelity_failures
        and not decode_failures
        and dt10["dt10_pass"]
        and dt11["dt11_pass"]
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(part for part in [env.get("PYTHONPATH"), str(ROOT), str(ROOT / "python")] if part)

    authority_verdict: dict
    if subset_pass:
        authority_verdict = _run_authority_benchmark(env)
        mean_cr = float(authority_verdict.get("mean_cr", 0.0))
        wins = int(authority_verdict.get("wins", 0))
        total = int(authority_verdict.get("total", 0))
        authority_verdict["passes_gate"] = mean_cr >= 5.0 and wins >= 7 and total >= 8
    else:
        authority_verdict = {
            "artifact": None,
            "passes_gate": False,
            "reason": "Subset guardrails did not clear, so a full E1 rerun was not justified.",
        }

    output = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "authority_artifact": str(AUTHORITY_BENCHMARK.relative_to(ROOT)),
        "fidelity_metric_mode": BENCHMARK_FIDELITY_MODE.value,
        "fidelity_metric_label": fidelity_label(BENCHMARK_FIDELITY_MODE),
        "mechanism": {
            "id": "count_aware_exact_fidelity_token_bitpack",
            "description": "Balanced and lossless packets use a count-aware compact bitstream while decode semantics remain unchanged.",
        },
        "subset_results": subset_results,
        "subset_acceptance": {
            "improved_dataset_count": improved_count,
            "minimum_required_improvements": 2,
            "fidelity_failures": fidelity_failures,
            "decode_failures": decode_failures,
            "dt10_pass": dt10["dt10_pass"],
            "dt11_pass": dt11["dt11_pass"],
            "retained": subset_pass,
        },
        "dt10": dt10,
        "dt11": dt11,
        "authority_projection_reference": {
            "authority_mean_cr": float(sum(float(row["zpe_iot_cr"]) for row in authority_rows.values()) / len(authority_rows)),
            "authority_wins": sum(1 for row in authority_rows.values() if row.get("winner") == "zpe-iot"),
            "authority_total": len(authority_rows),
        },
        "authority_verdict": authority_verdict,
        "verdict": {
            "retained": subset_pass,
            "summary": (
                "The exact-fidelity token-bitpack line stays live only if the subset improves without any fidelity, parity, or monotonicity regression. "
                "If that clears, the full E1 rerun becomes admissible; otherwise Phase 2 should be downgraded from the failed subset result."
            ),
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
