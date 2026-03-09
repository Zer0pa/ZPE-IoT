#!/usr/bin/env python3
"""Run ZH-1 ablation (derivative-domain byte shaping) on E1 datasets."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from validation.benchmarks._common import RESULTS_DIR, ds_preset
from validation.datasets.loader import load_dataset
from zpe_iot import compute_nrmse, decode, encode

MANIFEST = ROOT / "validation" / "datasets" / "manifest.json"
FLAG = "ZPE_IOT_ZH1_DERIVATIVE_STAGE"
THRESHOLD_CR_IMPROVEMENT = 0.08


@contextmanager
def _zh1_flag(enabled: bool):
    old = os.getenv(FLAG)
    try:
        if enabled:
            os.environ[FLAG] = "1"
        else:
            os.environ.pop(FLAG, None)
        yield
    finally:
        if old is None:
            os.environ.pop(FLAG, None)
        else:
            os.environ[FLAG] = old


def _e1_dataset_ids() -> list[str]:
    manifest = json.loads(MANIFEST.read_text())
    out = []
    for i in range(1, 9):
        ds_id = f"DS-{i:02d}"
        entry = manifest.get(ds_id, {})
        if str(entry.get("provenance_class", "")) == "real_public" and str(entry.get("status", "READY")).upper() == "READY":
            out.append(ds_id)
    return out


def _wire_metrics(samples: np.ndarray, preset: str, repeats: int, warmup: int) -> tuple[dict, list[float], list[float]]:
    samples = np.asarray(samples, dtype=np.float64)
    usable = (len(samples) // 256) * 256
    windows = samples[:usable].reshape(-1, 256) if usable else samples.reshape(1, -1)

    run_crs: list[float] = []
    run_nrmse: list[float] = []
    enc_times: list[float] = []
    dec_times: list[float] = []

    total_runs = max(0, int(warmup)) + max(1, int(repeats))
    for run_idx in range(total_runs):
        measure = run_idx >= max(0, int(warmup))
        raw_bytes = 0
        packed_bytes = 0
        errs: list[float] = []
        for w in windows:
            t0 = time.perf_counter()
            stream = encode(w, preset=preset)
            packet = stream.to_bytes()
            t1 = time.perf_counter()
            restored = decode(packet)
            t2 = time.perf_counter()

            raw_bytes += int(len(w) * 8)
            packed_bytes += int(len(packet))
            errs.append(float(compute_nrmse(w, restored)))
            if measure:
                enc_times.append((t1 - t0) * 1000.0)
                dec_times.append((t2 - t1) * 1000.0)

        if measure:
            run_crs.append(float(raw_bytes / max(1, packed_bytes)))
            run_nrmse.append(float(np.mean(errs) if errs else 0.0))

    metrics = {
        "cr": float(np.mean(run_crs) if run_crs else 0.0),
        "nrmse": float(np.mean(run_nrmse) if run_nrmse else 0.0),
        "encode_ms": float(np.mean(enc_times) if enc_times else 0.0),
        "decode_ms": float(np.mean(dec_times) if dec_times else 0.0),
        "encode_p50_ms": float(np.percentile(enc_times, 50) if enc_times else 0.0),
        "encode_p99_ms": float(np.percentile(enc_times, 99) if enc_times else 0.0),
        "decode_p50_ms": float(np.percentile(dec_times, 50) if dec_times else 0.0),
        "decode_p99_ms": float(np.percentile(dec_times, 99) if dec_times else 0.0),
    }
    return metrics, enc_times, dec_times


def _latest_dt_result(before: set[Path]) -> Path:
    after = set((ROOT / "validation" / "results").glob("dt_results_*.json"))
    new_files = sorted(after - before)
    if not new_files:
        raise RuntimeError("Strict DT run did not emit a dt_results artifact")
    return new_files[-1]


def _run_strict_dt(zh1_enabled: bool) -> dict:
    env = os.environ.copy()
    env[FLAG] = "1" if zh1_enabled else "0"
    before = set((ROOT / "validation" / "results").glob("dt_results_*.json"))
    cmd = [sys.executable, str(ROOT / "validation" / "destruct_tests" / "run_all_dts.py"), "--strict-gates"]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, env=env)
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    path: Path | None = None
    matches = re.findall(r"Saved:\s*(.+dt_results_[0-9T]+\.json)", out)
    if matches:
        path = Path(matches[-1].strip())
    if path is None or not path.exists():
        path = _latest_dt_result(before)
    payload = json.loads(path.read_text())
    failures = payload.get("mandatory_failures", [])
    return {
        "strict_rc": int(proc.returncode),
        "result_path": str(path),
        "mandatory_failures": failures,
        "strict_pass": bool(not failures),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--max-samples", type=int, default=256 * 128)
    args = parser.parse_args()

    ds_ids = _e1_dataset_ids()
    if not ds_ids:
        raise RuntimeError("No E1 datasets available for ZH-1 ablation")

    rows = []
    base_enc_all: list[float] = []
    base_dec_all: list[float] = []
    cand_enc_all: list[float] = []
    cand_dec_all: list[float] = []
    repeats = max(5, int(args.repeats))
    warmup = max(0, int(args.warmup))
    max_samples = max(256, int(args.max_samples))

    for ds_id in ds_ids:
        samples = load_dataset(ds_id)["samples"][:max_samples]
        preset = ds_preset(ds_id)
        with _zh1_flag(False):
            baseline, base_enc, base_dec = _wire_metrics(samples, preset=preset, repeats=repeats, warmup=warmup)
        with _zh1_flag(True):
            candidate, cand_enc, cand_dec = _wire_metrics(samples, preset=preset, repeats=repeats, warmup=warmup)

        base_enc_all.extend(base_enc)
        base_dec_all.extend(base_dec)
        cand_enc_all.extend(cand_enc)
        cand_dec_all.extend(cand_dec)

        rows.append(
            {
                "dataset": ds_id,
                "baseline": baseline,
                "zh1_candidate": candidate,
                "cr_improvement": (candidate["cr"] - baseline["cr"]) / max(1e-9, baseline["cr"]),
                "nrmse_delta": candidate["nrmse"] - baseline["nrmse"],
            }
        )

    base_mean_cr = float(np.mean([r["baseline"]["cr"] for r in rows]))
    cand_mean_cr = float(np.mean([r["zh1_candidate"]["cr"] for r in rows]))
    base_mean_nrmse = float(np.mean([r["baseline"]["nrmse"] for r in rows]))
    cand_mean_nrmse = float(np.mean([r["zh1_candidate"]["nrmse"] for r in rows]))
    cr_gain = (cand_mean_cr - base_mean_cr) / max(1e-9, base_mean_cr)
    nrmse_delta = cand_mean_nrmse - base_mean_nrmse

    strict_baseline = _run_strict_dt(zh1_enabled=False)
    strict_candidate = _run_strict_dt(zh1_enabled=True)
    base_fail = {(f.get("dt"), f.get("status")) for f in strict_baseline.get("mandatory_failures", [])}
    cand_fail = {(f.get("dt"), f.get("status")) for f in strict_candidate.get("mandatory_failures", [])}
    introduced = sorted(str(x) for x in (cand_fail - base_fail))
    gate_regression_detected = bool(
        (not strict_candidate["strict_pass"] and strict_baseline["strict_pass"])
        or len(cand_fail) > len(base_fail)
        or introduced
    )

    retained = cr_gain >= THRESHOLD_CR_IMPROVEMENT and nrmse_delta <= 1e-9 and not gate_regression_detected
    reason = (
        f"Retained: CR gain {cr_gain:.2%} >= {THRESHOLD_CR_IMPROVEMENT:.0%}, no NRMSE regression, strict gates unchanged"
        if retained
        else f"Rejected: gain={cr_gain:.2%}, nrmse_delta={nrmse_delta:.3e}, gate_regression_detected={gate_regression_detected}"
    )

    payload = {
        "timestamp": datetime.now().strftime("%Y%m%dT%H%M%S"),
        "workstream": "ZH-1",
        "threshold_cr_gain": THRESHOLD_CR_IMPROVEMENT,
        "datasets": rows,
        "mean_baseline_cr": base_mean_cr,
        "mean_candidate_cr": cand_mean_cr,
        "mean_cr_gain": cr_gain,
        "mean_baseline_nrmse": base_mean_nrmse,
        "mean_candidate_nrmse": cand_mean_nrmse,
        "mean_nrmse_delta": nrmse_delta,
        "aggregate_latency_wire_ms": {
            "baseline_encode_p50_ms": float(np.percentile(base_enc_all, 50) if base_enc_all else 0.0),
            "baseline_encode_p99_ms": float(np.percentile(base_enc_all, 99) if base_enc_all else 0.0),
            "baseline_decode_p50_ms": float(np.percentile(base_dec_all, 50) if base_dec_all else 0.0),
            "baseline_decode_p99_ms": float(np.percentile(base_dec_all, 99) if base_dec_all else 0.0),
            "candidate_encode_p50_ms": float(np.percentile(cand_enc_all, 50) if cand_enc_all else 0.0),
            "candidate_encode_p99_ms": float(np.percentile(cand_enc_all, 99) if cand_enc_all else 0.0),
            "candidate_decode_p50_ms": float(np.percentile(cand_dec_all, 50) if cand_dec_all else 0.0),
            "candidate_decode_p99_ms": float(np.percentile(cand_dec_all, 99) if cand_dec_all else 0.0),
        },
        "retained": retained,
        "reason": reason,
        "feature_flag": FLAG,
        "default_enabled": False,
        "gate_regression_detected": gate_regression_detected,
        "strict_gate_differential": {
            "baseline": strict_baseline,
            "candidate": strict_candidate,
            "introduced_failures": introduced,
        },
        "measurement_protocol": {
            "pathway": "encode_to_packet_bytes_then_decode_from_packet_bytes",
            "repeats": repeats,
            "warmup": warmup,
            "window_size": 256,
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"zh1_ablation_{payload['timestamp']}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Saved: {out}")
    print(reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
