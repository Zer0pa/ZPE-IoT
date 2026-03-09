#!/usr/bin/env python3
"""DT-25: Chemosense malformed-packet resilience + provenance floor."""

from __future__ import annotations

import json
import subprocess
import sys

from _common import ROOT, log_result, print_case
from zpe_iot.chemosense import ChemosensePacketError, decode_smell_payload, decode_taste_payload


MALFORMED_CASES = [
    [0x0001, 0x0002, 0x0003],
    [0x20000, 0x20001],
    [0x12345],
]


def _decode_rejects_invalid() -> tuple[bool, list[str]]:
    issues: list[str] = []

    for idx, words in enumerate(MALFORMED_CASES):
        try:
            decode_smell_payload(words)
            issues.append(f"smell decoder accepted malformed case {idx}")
        except ChemosensePacketError:
            pass

        try:
            decode_taste_payload(words)
            issues.append(f"taste decoder accepted malformed case {idx}")
        except ChemosensePacketError:
            pass

    return (len(issues) == 0), issues


def _provenance_ok() -> tuple[bool, str]:
    cmd = [
        sys.executable,
        str(ROOT / "validation" / "datasets" / "verify_chemosense_provenance.py"),
        "--min-class",
        "E1",
    ]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, output[-1000:]


def _latest_chemo_bench() -> tuple[bool, str]:
    files = sorted((ROOT / "validation" / "results").glob("bench_summary_chemosense_*.json"))
    if not files:
        return False, "missing bench_summary_chemosense artifact"

    latest = files[-1]
    try:
        payload = json.loads(latest.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"failed to parse {latest.name}: {exc}"

    baseline_tag = str(payload.get("baseline_tag") or "").strip()
    datasets = payload.get("datasets", [])
    if not baseline_tag:
        return False, f"{latest.name} missing baseline_tag"
    if not isinstance(datasets, list) or len(datasets) < 3:
        return False, f"{latest.name} has insufficient dataset rows"
    return True, f"verified {latest.name} baseline_tag={baseline_tag}"


def main() -> int:
    ok_decode, decode_issues = _decode_rejects_invalid()
    ok_prov, prov_output = _provenance_ok()
    ok_bench, bench_output = _latest_chemo_bench()

    if not ok_decode:
        for issue in decode_issues:
            print_case("FAIL", issue)

    if not ok_prov:
        print_case("FAIL", "Chemosense provenance verification failed")

    if not ok_bench:
        print_case("FAIL", "Chemosense benchmark artifact/baseline metadata check failed")

    if not ok_decode or not ok_prov or not ok_bench:
        notes = "; ".join(decode_issues + [prov_output, bench_output])
        log_result(
            "DT-25",
            "FAIL",
            {
                "decode_ok": int(ok_decode),
                "provenance_ok": int(ok_prov),
                "benchmark_ok": int(ok_bench),
            },
            notes=notes,
        )
        return 1

    print_case("PASS", "Malformed packets are rejected, provenance floor is E1, and chemosense benchmark baseline metadata is pinned")
    log_result(
        "DT-25",
        "PASS",
        {
            "decode_cases": len(MALFORMED_CASES),
            "provenance_min_class": "E1",
            "benchmark_baseline_pinned": 1,
        },
        notes=bench_output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
