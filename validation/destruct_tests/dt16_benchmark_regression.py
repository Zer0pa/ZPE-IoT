#!/usr/bin/env python3
"""DT-16: Benchmark Regression. PASS if no benchmark metric degrades >5% vs baseline."""

from __future__ import annotations

import json
from pathlib import Path

from _common import ROOT, log_result, print_case


def _latest(pattern: str) -> Path | None:
    files = sorted((ROOT / "validation" / "results").glob(pattern))
    return files[-1] if files else None


def main() -> int:
    baseline = _latest("baseline/bench_summary_*.json")
    current = _latest("bench_summary_*.json")

    if baseline is None or current is None:
        print_case("SKIP", "Missing baseline or current benchmark; cannot compare")
        log_result("DT-16", "SKIPPED", {}, notes="missing benchmark artifacts")
        return 0

    b = json.loads(baseline.read_text())
    c = json.loads(current.read_text())

    b_cr = float(b.get("mean_cr", 0.0))
    c_cr = float(c.get("mean_cr", 0.0))
    if b_cr <= 0:
        print_case("SKIP", "Invalid baseline mean_cr")
        log_result("DT-16", "SKIPPED", {}, notes="invalid baseline")
        return 0

    degradation = (b_cr - c_cr) / b_cr
    ok = degradation <= 0.05
    print_case("PASS" if ok else "FAIL", f"degradation={degradation:.2%}")
    log_result("DT-16", "PASS" if ok else "FAIL", {"degradation": degradation})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
