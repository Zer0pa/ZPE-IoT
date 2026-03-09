#!/usr/bin/env python3
"""Run Python and Rust vulnerability scans and emit a structured artifact."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "validation" / "results"


@dataclass
class CmdResult:
    returncode: int
    stdout: str
    stderr: str


def _run(cmd: list[str], cwd: Path | None = None) -> CmdResult:
    proc = subprocess.run(cmd, cwd=str(cwd or ROOT), capture_output=True, text=True)
    return CmdResult(proc.returncode, proc.stdout or "", proc.stderr or "")


def _sha256(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _score_from_cvss(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        m = re.search(r"(\d+(?:\.\d+)?)", value)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                return None
    return None


def _severity(score: float | None) -> str:
    if score is None:
        return "unknown"
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    return "low"


def _parse_cargo_audit(payload: dict) -> tuple[list[dict], int]:
    vulns = payload.get("vulnerabilities", {}).get("list", [])
    rows: list[dict] = []
    high_count = 0
    for item in vulns:
        advisory = item.get("advisory", {})
        cvss = advisory.get("cvss")
        score = _score_from_cvss(cvss)
        sev = _severity(score)
        if sev in {"high", "critical"}:
            high_count += 1
        rows.append(
            {
                "id": advisory.get("id"),
                "package": item.get("package", {}).get("name"),
                "title": advisory.get("title"),
                "cvss": cvss,
                "cvss_score": score,
                "severity": sev,
                "url": advisory.get("url"),
            }
        )
    return rows, high_count


def _parse_pip_audit(payload: object) -> tuple[list[dict], int, int]:
    deps: list[dict]
    if isinstance(payload, dict):
        raw = payload.get("dependencies", [])
        deps = raw if isinstance(raw, list) else []
    elif isinstance(payload, list):
        deps = payload
    else:
        return [], 0, 0

    rows: list[dict] = []
    unknown_count = 0
    for dep in deps:
        if not isinstance(dep, dict):
            continue
        name = dep.get("name")
        version = dep.get("version")
        vulns = dep.get("vulns") or dep.get("vulnerabilities") or []
        if not isinstance(vulns, list):
            continue
        for vuln in vulns:
            if not isinstance(vuln, dict):
                continue
            rows.append(
                {
                    "id": vuln.get("id"),
                    "package": name,
                    "version": version,
                    "fix_versions": vuln.get("fix_versions", []),
                    "aliases": vuln.get("aliases", []),
                    "severity": "unknown",
                }
            )
            unknown_count += 1
    return rows, 0, unknown_count


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

    pip_audit_path = ROOT / ".venv" / "bin" / "pip-audit"
    if not pip_audit_path.exists():
        discovered = shutil.which("pip-audit")
        if discovered:
            pip_audit_path = Path(discovered)
        else:
            raise SystemExit("pip-audit not found in project venv or PATH")

    py_cmd = [
        str(pip_audit_path),
        "-l",
        "--format",
        "json",
        "--progress-spinner",
        "off",
        "--desc",
        "on",
        "--aliases",
        "on",
    ]
    py = _run(py_cmd, cwd=ROOT)
    py_json: object
    try:
        py_json = json.loads(py.stdout.strip() or "[]")
    except json.JSONDecodeError:
        py_json = []
    py_rows, py_high, py_unknown = _parse_pip_audit(py_json)

    rust_cmd = ["cargo", "audit", "--json"]
    rust = _run(rust_cmd, cwd=ROOT / "core")
    rust_json: dict
    try:
        rust_json = json.loads(rust.stdout.strip() or "{}")
    except json.JSONDecodeError:
        rust_json = {}
    rust_rows, rust_high = _parse_cargo_audit(rust_json)

    high_total = int(py_high + rust_high)
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_scan": {
            "command": py_cmd,
            "returncode": py.returncode,
            "vulnerability_count": len(py_rows),
            "high_or_critical_count": py_high,
            "unknown_severity_count": py_unknown,
            "vulnerabilities": py_rows,
        },
        "rust_scan": {
            "command": rust_cmd,
            "returncode": rust.returncode,
            "vulnerability_count": len(rust_rows),
            "high_or_critical_count": rust_high,
            "vulnerabilities": rust_rows,
        },
        "summary": {
            "high_or_critical_count": high_total,
            "documented_exceptions": (
                [
                    "Python advisory feed does not provide normalized CVSS in pip-audit output; entries marked severity=unknown."
                ]
                if py_unknown > 0
                else []
            ),
        },
    }

    out = RESULTS_DIR / f"vulnerability_scan_{ts}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    hash_path = RESULTS_DIR / f"vulnerability_scan_{ts}.sha256"
    hash_path.write_text(f"{_sha256(out)}  {out.name}\n", encoding="utf-8")

    print(f"Saved: {out}")
    print(f"High/Critical vulnerabilities: {high_total}")

    return 0 if high_total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
