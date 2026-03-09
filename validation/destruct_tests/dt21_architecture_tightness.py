#!/usr/bin/env python3
"""DT-21: Architecture Tightness. Check for known circuitous patterns."""

from __future__ import annotations

from pathlib import Path

from _common import ROOT, log_result, print_case


def _count(text: str, needle: str) -> int:
    return text.count(needle)


def main() -> int:
    issues: list[str] = []

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    customer_demo = (ROOT / "scripts" / "customer_demo.py").read_text(encoding="utf-8")
    dt06 = (ROOT / "validation" / "destruct_tests" / "dt06_ram_budget.py").read_text(encoding="utf-8")
    dt16 = (ROOT / "validation" / "destruct_tests" / "dt16_benchmark_regression.py").read_text(encoding="utf-8")
    fusion_scheduler = (ROOT / "python" / "zpe_iot" / "chemosense" / "taste" / "fusion_scheduler.py").read_text(
        encoding="utf-8"
    )
    native_py = (ROOT / "python" / "zpe_iot" / "_native.py").read_text(encoding="utf-8")
    audit_doc = ROOT / "docs" / "ARCH_TIGHTNESS_AUDIT.md"

    if _count(readme, "encode(signal") > 1:
        issues.append("README quickstart performs repeated encode(signal) work")

    for baseline in ("zstd", "lz4", "zlib"):
        if baseline not in customer_demo:
            issues.append(f"customer_demo missing side-by-side baseline `{baseline}`")

    if "ram_bytes_proxy" in dt06 or "proxy measurement" in dt06:
        issues.append("DT-06 still contains PASS-on-proxy logic")

    if "_latest(\"baseline/bench_summary_" in dt16:
        issues.append("DT-16 still uses floating latest baseline behavior")
    if "--baseline-tag" not in dt16:
        issues.append("DT-16 missing explicit baseline-tag contract")

    if "_extract_taste_packets(self._raw_stream)" in fusion_scheduler:
        issues.append("Chemosense fusion scheduler still performs separate full-stream taste scan")
    if "_extract_smell_packets(self._raw_stream)" in fusion_scheduler:
        issues.append("Chemosense fusion scheduler still performs separate full-stream smell scan")
    if "_extract_touch_packets(self._raw_stream)" in fusion_scheduler:
        issues.append("Chemosense fusion scheduler still performs separate full-stream touch scan")

    if "x.tolist()" in native_py and "_FFI.new(\"double[]\"" in native_py:
        issues.append("Native encode path still materializes Python list per call")

    if not audit_doc.exists():
        issues.append("docs/ARCH_TIGHTNESS_AUDIT.md is missing")

    if issues:
        for issue in issues:
            print_case("FAIL", issue)
        log_result("DT-21", "FAIL", {"issues": len(issues)}, notes="; ".join(issues))
        return 1

    print_case("PASS", "Architecture tightness constraints satisfied")
    log_result("DT-21", "PASS", {"issues": 0})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
