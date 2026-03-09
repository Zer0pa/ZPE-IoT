#!/usr/bin/env python3
"""DT-16: Benchmark Regression. PASS if no benchmark metric degrades >5% vs baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from _common import ROOT, log_result, print_case
from thresholds import BENCHMARK_REGRESSION_MAX_DEGRADATION

BASELINE_ROOT = ROOT / "validation" / "results" / "baseline"
ACTIVE_TAG_FILE = BASELINE_ROOT / "ACTIVE_BASELINE_TAG"


def _latest(pattern: str) -> Path | None:
    files = sorted((ROOT / "validation" / "results").glob(pattern))
    return files[-1] if files else None


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve_baseline_tag(arg_tag: str | None) -> str | None:
    if arg_tag:
        return arg_tag.strip()
    env_tag = os.getenv("ZPE_IOT_BASELINE_TAG", "").strip()
    if env_tag:
        return env_tag
    if ACTIVE_TAG_FILE.exists():
        file_tag = ACTIVE_TAG_FILE.read_text(encoding="utf-8").strip()
        if file_tag:
            return file_tag
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-tag", type=str, default=None)
    args = parser.parse_args()

    baseline_tag = _resolve_baseline_tag(args.baseline_tag)

    if not baseline_tag:
        print_case("FAIL", "Missing baseline_tag (arg/env/ACTIVE_BASELINE_TAG)")
        log_result("DT-16", "FAIL", {}, notes="missing baseline_tag")
        return 1

    baseline_dir = BASELINE_ROOT / baseline_tag
    baseline = baseline_dir / "bench_summary.json"
    manifest = baseline_dir / "manifest.json"

    if not baseline.exists() or not manifest.exists():
        print_case("FAIL", f"Invalid baseline tag `{baseline_tag}` (missing bench_summary.json or manifest.json)")
        log_result("DT-16", "FAIL", {"baseline_tag": baseline_tag}, notes="invalid baseline tag path")
        return 1

    try:
        m = json.loads(manifest.read_text())
    except Exception as exc:
        print_case("FAIL", f"Baseline manifest unreadable: {exc}")
        log_result("DT-16", "FAIL", {"baseline_tag": baseline_tag}, notes=f"bad manifest: {exc}")
        return 1

    expected_hash = str(m.get("bench_summary_sha256", "")).strip()
    actual_hash = _sha256(baseline)
    if expected_hash != actual_hash:
        print_case("FAIL", "Baseline hash mismatch; baseline artifact is not immutable")
        log_result(
            "DT-16",
            "FAIL",
            {"baseline_tag": baseline_tag},
            notes=f"hash mismatch expected={expected_hash} actual={actual_hash}",
        )
        return 1

    current = _latest("bench_summary_[0-9]*.json")

    if current is None:
        print_case("FAIL", "Missing current benchmark summary")
        log_result("DT-16", "FAIL", {"baseline_tag": baseline_tag}, notes="missing current benchmark")
        return 1

    b = json.loads(baseline.read_text())
    c = json.loads(current.read_text())

    b_cr = float(b.get("mean_cr", 0.0))
    c_cr = float(c.get("mean_cr", 0.0))
    if b_cr <= 0:
        print_case("FAIL", "Invalid baseline mean_cr")
        log_result("DT-16", "FAIL", {"baseline_tag": baseline_tag}, notes="invalid baseline mean_cr")
        return 1

    degradation = (b_cr - c_cr) / b_cr
    ok = degradation <= BENCHMARK_REGRESSION_MAX_DEGRADATION
    print_case("PASS" if ok else "FAIL", f"baseline_tag={baseline_tag} degradation={degradation:.2%}")
    log_result(
        "DT-16",
        "PASS" if ok else "FAIL",
        {"degradation": degradation, "baseline_tag": baseline_tag},
        notes=f"baseline={baseline} current={current}",
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
