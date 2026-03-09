#!/usr/bin/env python3
"""DT-20: Workstream Ablation integrity for WI-1 experimental branch."""

from __future__ import annotations

import json
from pathlib import Path

from _common import ROOT, log_result, print_case
from thresholds import WI1_MIN_CR_GAIN


THRESHOLD = WI1_MIN_CR_GAIN


def _latest_wi1() -> Path | None:
    files = sorted((ROOT / "validation" / "results").glob("wi1_ablation_*.json"))
    return files[-1] if files else None


def main() -> int:
    path = _latest_wi1()
    if path is None:
        print_case("SKIP", "No WI-1 ablation artifact found")
        log_result("DT-20", "SKIPPED", {}, notes="missing wi1_ablation artifact")
        return 0

    payload = json.loads(path.read_text())
    gain = float(payload.get("mean_cr_gain", 0.0))
    nrmse_delta = float(payload.get("mean_nrmse_delta", 0.0))
    retained = bool(payload.get("retained", False))
    default_enabled = bool(payload.get("default_enabled", False))
    gate_regression = bool(payload.get("gate_regression_detected", False))
    protocol = payload.get("measurement_protocol", {})
    repeats = int(protocol.get("repeats", 0))
    pathway = str(protocol.get("pathway", ""))
    strict_diff = payload.get("strict_gate_differential", {})

    if repeats < 5 or "encode_to_packet_bytes_then_decode_from_packet_bytes" not in pathway:
        print_case("FAIL", "WI-1 artifact does not satisfy wire-path repeat protocol (repeats>=5)")
        log_result(
            "DT-20",
            "FAIL",
            {"gain": gain, "repeats": repeats},
            notes=f"artifact={path}; pathway={pathway}",
        )
        return 1

    if not isinstance(strict_diff, dict) or "baseline" not in strict_diff or "candidate" not in strict_diff:
        print_case("FAIL", "WI-1 artifact missing strict gate differential payload")
        log_result("DT-20", "FAIL", {"gain": gain}, notes=f"artifact={path}; missing strict differential")
        return 1

    if retained:
        ok = gain >= THRESHOLD and nrmse_delta <= 1e-9 and not gate_regression
        if ok:
            print_case("PASS", f"Retained WI-1 with gain={gain:.2%}, nrmse_delta={nrmse_delta:.3e}")
            log_result("DT-20", "PASS", {"gain": gain, "nrmse_delta": nrmse_delta})
            return 0
        print_case("FAIL", "Retained WI-1 does not satisfy threshold or regression constraints")
        log_result(
            "DT-20",
            "FAIL",
            {"gain": gain, "nrmse_delta": nrmse_delta, "gate_regression": int(gate_regression)},
            notes=f"artifact={path}",
        )
        return 1

    # Rejected candidate is acceptable if it remains off by default and explicitly documented.
    if not default_enabled:
        print_case("PASS", f"Rejected WI-1 candidate (gain={gain:.2%}, nrmse_delta={nrmse_delta:.3e})")
        log_result("DT-20", "PASS", {"gain": gain, "nrmse_delta": nrmse_delta, "retained": 0}, notes=f"artifact={path}")
        return 0

    print_case("FAIL", "WI-1 rejected but still enabled by default")
    log_result("DT-20", "FAIL", {"gain": gain, "default_enabled": int(default_enabled)}, notes=f"artifact={path}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
