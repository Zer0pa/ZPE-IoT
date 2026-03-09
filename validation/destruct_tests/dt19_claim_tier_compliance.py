#!/usr/bin/env python3
"""DT-19: Claim-Tier Compliance. Enforce evidence-class truthful claims."""

from __future__ import annotations

import json
from pathlib import Path

from _common import ROOT, log_result, print_case


def _evidence_class() -> str:
    manifest = json.loads((ROOT / "validation" / "datasets" / "manifest.json").read_text())
    classes = {str(manifest[f"DS-{i:02d}"]["provenance_class"]) for i in range(1, 9)}
    if "real_customer" in classes:
        return "E2"
    if classes == {"proxy"}:
        return "E0"
    if "real_public" in classes:
        return "E1"
    return "E0"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _latest(prefix: str) -> Path | None:
    files = sorted((ROOT / "validation" / "results").glob(f"{prefix}_*.json"))
    return files[-1] if files else None


def _validate_label_rule(payload: dict) -> str | None:
    total = int(payload.get("total", 0))
    evidence = str(payload.get("evidence_class", "E0"))
    label = str(payload.get("pt6_label", ""))
    status = str(payload.get("pt6_status", ""))

    if total == 0:
        if label != "NOT_AVAILABLE" or status != "NOT_AVAILABLE":
            return f"{evidence} with total=0 must be NOT_AVAILABLE/NOT_AVAILABLE, got {label}/{status}"
        return None

    if evidence == "E0":
        if label != "PROVISIONAL":
            return f"E0 with data must be PROVISIONAL, got {label}"
    else:
        if label != "FINAL":
            return f"{evidence} with data must be FINAL, got {label}"
    if status not in {"PASS", "FAIL"}:
        return f"{evidence} with data must have PASS/FAIL status, got {status}"
    return None


def main() -> int:
    bench_md = _read(ROOT / "docs" / "BENCHMARKS.md")
    sales_md = _read(ROOT / "docs" / "ZPE_IOT_SALES_BRIEF.md")
    outreach_md = _read(ROOT / "docs" / "OUTREACH_TEMPLATE.md")
    bench_plain = bench_md.replace("*", "")

    evidence = _evidence_class()
    issues: list[str] = []

    if "Evidence Class:" not in bench_plain:
        issues.append("docs/BENCHMARKS.md missing `Evidence Class:` label")

    if evidence == "E0":
        if "PROVISIONAL" not in bench_md:
            issues.append("E0 requires PROVISIONAL benchmark labeling")
        if "PT-6 FINAL" in bench_md:
            issues.append("E0 cannot claim PT-6 FINAL")
    else:
        if f"Evidence Class: {evidence}" not in bench_plain:
            issues.append(f"docs/BENCHMARKS.md must state `Evidence Class: {evidence}`")
        if "PT-6 PROVISIONAL" in bench_md and "PT-6 FINAL" not in bench_md:
            issues.append("E1/E2 should not remain only PROVISIONAL")

    if f"({evidence})" not in sales_md:
        issues.append(f"docs/ZPE_IOT_SALES_BRIEF.md missing claim-tier marker ({evidence})")
    if f"({evidence})" not in outreach_md:
        issues.append(f"docs/OUTREACH_TEMPLATE.md missing claim-tier marker ({evidence})")

    for prefix in ("bench_summary_E0_proxy", "bench_summary_E1_real_public", "bench_summary_E2_real_customer"):
        path = _latest(prefix)
        if path is None:
            issues.append(f"Missing benchmark split summary for {prefix}")
            continue
        err = _validate_label_rule(json.loads(path.read_text()))
        if err:
            issues.append(f"{path.name}: {err}")

    if issues:
        for issue in issues:
            print_case("FAIL", issue)
        log_result("DT-19", "FAIL", {"issues": len(issues)}, notes="; ".join(issues))
        return 1

    print_case("PASS", f"Claim tier compliance verified for {evidence}")
    log_result("DT-19", "PASS", {"evidence_class": evidence})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
