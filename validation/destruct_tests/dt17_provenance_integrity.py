#!/usr/bin/env python3
"""DT-17: Provenance Integrity. PASS only if DS-01..DS-08 provenance is verified."""

from __future__ import annotations

import subprocess
import sys

from _common import ROOT, log_result, print_case


def main() -> int:
    cmd = [
        sys.executable,
        str(ROOT / "validation" / "datasets" / "verify_provenance.py"),
        "--min-class",
        "real_public",
    ]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    out = (proc.stdout + proc.stderr).strip()
    if out:
        print(out)

    if proc.returncode == 0:
        print_case("PASS", "DS-01..DS-08 provenance manifest and hashes verified")
        log_result("DT-17", "PASS", {"returncode": 0})
        return 0

    if "[BLOCKED]" in out:
        print_case("BLOCKED", "One or more required datasets are explicitly blocked")
        log_result("DT-17", "BLOCKED", {"returncode": proc.returncode}, notes=out[-1000:])
        return 0

    print_case("FAIL", "Provenance verification failed")
    log_result("DT-17", "FAIL", {"returncode": proc.returncode}, notes=out[-1000:])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
