#!/usr/bin/env python3
"""Run the bounded Phase 6 DS-05 zero-special packet probe."""

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
from zpe_iot import decode, encode
from zpe_iot import _native
from zpe_iot.codec import PACKET_MAGIC_ZERO_SPECIAL, pack_stream

AUTHORITY_BENCHMARK = ROOT / "validation" / "results" / "bench_summary_E1_real_public_20260321T144350.json"
OUTPUT = ROOT / "proofs" / "artifacts" / "PHASE6_DS05_STRUCTURAL_PROBE_20260321.json"
RUN_BENCHMARKS = ROOT / "validation" / "benchmarks" / "run_benchmarks.py"

DATASETS = tuple(f"DS-{i:02d}" for i in range(1, 9))
WINDOW_SIZE = 256
MAX_WINDOWS = 64
FIDELITY_EPSILON = 1e-12
THRESHOLDS = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]


def _windowed(samples: np.ndarray) -> np.ndarray:
    usable = min(len(samples) // WINDOW_SIZE, MAX_WINDOWS) * WINDOW_SIZE
    clipped = np.asarray(samples[:usable], dtype=np.float64)
    if usable == 0:
        raise RuntimeError("Need at least one full 256-sample window for the DS-05 probe")
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


def _iter_chunks(rle_tokens):
    for d, m, count in rle_tokens:
        remaining = int(count)
        while remaining > 0:
            chunk = min(remaining, 127)
            yield int(d), int(m), chunk
            remaining -= chunk


def _dataset_row(ds_id: str) -> dict:
    windows = _windowed(load_dataset(ds_id)["samples"])

    raw_total_bytes = 0
    baseline_total_bytes = 0
    candidate_total_bytes = 0
    baseline_errs: list[float] = []
    candidate_errs: list[float] = []
    decode_match = True
    zero_special_windows = 0
    zero_count1_chunks = 0
    zero_run_chunks = 0
    total_chunks = 0

    for window in windows:
        stream = encode(window, preset=ds_preset(ds_id))
        baseline_packet = pack_stream(stream, compact=True, zero_special=False)
        candidate_packet = stream.to_bytes()

        baseline_restored = decode(baseline_packet)
        candidate_restored = decode(candidate_packet)

        raw_total_bytes += len(window) * 8
        baseline_total_bytes += len(baseline_packet)
        candidate_total_bytes += len(candidate_packet)
        baseline_errs.append(nrmse(window, baseline_restored, mode=BENCHMARK_FIDELITY_MODE))
        candidate_errs.append(nrmse(window, candidate_restored, mode=BENCHMARK_FIDELITY_MODE))
        decode_match = decode_match and np.allclose(baseline_restored, candidate_restored, rtol=0.0, atol=1e-12)

        if candidate_packet[:2] == PACKET_MAGIC_ZERO_SPECIAL.to_bytes(2, "little"):
            zero_special_windows += 1

        for d, m, count in _iter_chunks(stream.rle_tokens):
            total_chunks += 1
            if d == 0 and m == 0 and count == 1:
                zero_count1_chunks += 1
            elif d == 0 and m == 0:
                zero_run_chunks += 1

    baseline_cr = float(raw_total_bytes / max(1, baseline_total_bytes))
    candidate_cr = float(raw_total_bytes / max(1, candidate_total_bytes))
    baseline_nrmse = float(np.mean(baseline_errs))
    candidate_nrmse = float(np.mean(candidate_errs))

    return {
        "dataset": ds_id,
        "preset": ds_preset(ds_id),
        "window_count": int(len(windows)),
        "baseline_compression_ratio": baseline_cr,
        "candidate_compression_ratio": candidate_cr,
        "compression_ratio_gain": candidate_cr - baseline_cr,
        "baseline_total_bytes": int(baseline_total_bytes),
        "candidate_total_bytes": int(candidate_total_bytes),
        "compressed_byte_delta": int(candidate_total_bytes - baseline_total_bytes),
        "baseline_nrmse": baseline_nrmse,
        "candidate_nrmse": candidate_nrmse,
        "nrmse_delta": candidate_nrmse - baseline_nrmse,
        "decode_match": decode_match,
        "zero_special_windows": int(zero_special_windows),
        "zero_special_window_share": zero_special_windows / max(1, len(windows)),
        "zero_count1_chunk_share": zero_count1_chunks / max(1, total_chunks),
        "zero_run_chunk_share": zero_run_chunks / max(1, total_chunks),
        "acceptance": {
            "improved_or_equal": candidate_total_bytes <= baseline_total_bytes,
            "strict_improved": candidate_total_bytes < baseline_total_bytes,
            "fidelity_guardrail_pass": abs(candidate_nrmse - baseline_nrmse) <= FIDELITY_EPSILON,
            "decode_match": decode_match,
        },
    }


def _dt10_row() -> dict:
    samples = load_dataset("DS-02")["samples"][:20_480]
    rows = []
    for threshold in THRESHOLDS:
        raw_total = 0
        payload_total = 0
        for start in range(0, len(samples), WINDOW_SIZE):
            window = samples[start : start + WINDOW_SIZE]
            if len(window) < WINDOW_SIZE:
                break
            stream = encode(window, preset="vibration", threshold=threshold, mode="balanced")
            packet = stream.to_bytes()
            raw_total += len(window) * 8
            payload_total += len(packet)
        rows.append(
            {
                "threshold": threshold,
                "compression_ratio": float(raw_total / max(1, payload_total)),
                "packet_bytes": int(payload_total),
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
    from zpe_iot import Config  # imported lazily to keep script startup small

    config = Config.from_preset("vibration")
    mismatch_index = None
    for idx in range(100):
        x = rng.standard_normal(256)
        py_packet = encode(x, config=config).to_bytes()
        rs_packet = _native.encode(x, config=config)
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
        result["datasets"] = payload.get("datasets", [])
    return result


def main() -> int:
    authority_rows = _authority_rows()
    dataset_rows = [_dataset_row(ds_id) for ds_id in DATASETS]

    fidelity_failures = [row["dataset"] for row in dataset_rows if not row["acceptance"]["fidelity_guardrail_pass"]]
    decode_failures = [row["dataset"] for row in dataset_rows if not row["acceptance"]["decode_match"]]
    regressions = [row["dataset"] for row in dataset_rows if not row["acceptance"]["improved_or_equal"]]

    ds05_row = next(row for row in dataset_rows if row["dataset"] == "DS-05")
    authority_ds05 = authority_rows["DS-05"]
    ds05_zlib_cr = float(authority_ds05["zlib_cr"])

    dt10 = _dt10_row()
    dt11 = _dt11_row()

    subset_pass = (
        not fidelity_failures
        and not decode_failures
        and not regressions
        and dt10["dt10_pass"]
        and dt11["dt11_pass"]
        and ds05_row["candidate_compression_ratio"] > ds05_zlib_cr
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(part for part in [env.get("PYTHONPATH"), str(ROOT), str(ROOT / "python")] if part)

    authority_verdict: dict
    if subset_pass:
        authority_verdict = _run_authority_benchmark(env)
        mean_cr = float(authority_verdict.get("mean_cr", 0.0))
        wins = int(authority_verdict.get("wins", 0))
        total = int(authority_verdict.get("total", 0))
        authority_verdict["passes_gate"] = (
            authority_verdict.get("returncode", 1) == 0 and mean_cr >= 6.5 and wins >= 7 and total >= 8
        )
    else:
        authority_verdict = {
            "artifact": None,
            "passes_gate": False,
            "reason": "Phase 6 guardrails did not clear, so a full authority rerun was not justified.",
        }

    output = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "authority_artifact": str(AUTHORITY_BENCHMARK.relative_to(ROOT)),
        "fidelity_metric_mode": BENCHMARK_FIDELITY_MODE.value,
        "fidelity_metric_label": fidelity_label(BENCHMARK_FIDELITY_MODE),
        "mechanism": {
            "id": "zero_special_exact_fidelity_packet_route",
            "description": "Balanced packets may switch to a zero-special compact payload only when it is strictly smaller than the current compact wire format.",
        },
        "datasets": dataset_rows,
        "guardrails": {
            "fidelity_failures": fidelity_failures,
            "decode_failures": decode_failures,
            "compression_regressions": regressions,
            "dt10_pass": dt10["dt10_pass"],
            "dt11_pass": dt11["dt11_pass"],
            "ds05_candidate_cr": ds05_row["candidate_compression_ratio"],
            "ds05_authority_zlib_cr": ds05_zlib_cr,
            "retained": subset_pass,
        },
        "dt10": dt10,
        "dt11": dt11,
        "authority_verdict": authority_verdict,
        "verdict": {
            "retained": subset_pass,
            "summary": (
                "Phase 6 stays live only if the zero-special packet route remains exact-fidelity, preserves DT-10 and DT-11, never regresses any E1 dataset, "
                "and overturns the DS-05 zlib loss before the authority rerun."
            ),
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
