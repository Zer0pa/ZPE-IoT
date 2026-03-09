#!/usr/bin/env python3
"""DT-26: Import hygiene guard for local chemosense touch/mental integration."""

from __future__ import annotations

import subprocess

from _common import ROOT, log_result, print_case

CHEMOSENSE_DIR = ROOT / "python" / "zpe_iot" / "chemosense"
PATTERN = r"from source\\.|import source\\.|artifacts\\.packetgram"


def main() -> int:
    cmd = ["rg", "-n", PATTERN, str(CHEMOSENSE_DIR)]
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    except FileNotFoundError:
        print_case("FAIL", "rg is not available for import-hygiene enforcement")
        log_result("DT-26", "FAIL", {"matches": -1}, notes="missing rg executable")
        return 1

    if proc.returncode == 1:
        print_case("PASS", "No forbidden import or artifact path references found in chemosense tree")
        log_result("DT-26", "PASS", {"matches": 0, "path": str(CHEMOSENSE_DIR)})
        return 0

    if proc.returncode == 0:
        output = (proc.stdout + proc.stderr).strip()
        print_case("FAIL", "Forbidden import/artifact references found")
        log_result(
            "DT-26",
            "FAIL",
            {"matches": len([line for line in proc.stdout.splitlines() if line.strip()])},
            notes=output[-2000:],
        )
        return 1

    output = (proc.stdout + proc.stderr).strip()
    print_case("FAIL", f"rg returned unexpected status: {proc.returncode}")
    log_result("DT-26", "FAIL", {"matches": -2, "returncode": proc.returncode}, notes=output[-1000:])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
