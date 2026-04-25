#!/usr/bin/env python3
"""DT-17: Provenance Integrity.

PASS only if READY datasets verify cleanly and any explicitly BLOCKED datasets
remain declared as blocked on the active strict surface.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from _common import ROOT, log_result, print_case

MANIFEST_PATH = ROOT / "validation" / "datasets" / "manifest.json"


def _load_dataset_sets() -> tuple[list[str], list[str]]:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    ready: list[str] = []
    blocked: list[str] = []
    for ds_id in sorted((key for key in payload if key.startswith("DS-")), key=lambda value: int(value.split("-")[1])):
        status = str(payload[ds_id].get("status", "READY")).upper()
        if status == "BLOCKED":
            blocked.append(ds_id)
        else:
            ready.append(ds_id)
    return ready, blocked


def _verify(*extra_args: str) -> subprocess.CompletedProcess[str]:
    cmd = [
        sys.executable,
        str(ROOT / "validation" / "datasets" / "verify_provenance.py"),
        "--min-class",
        "real_public",
        *extra_args,
    ]
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)


def main() -> int:
    if not MANIFEST_PATH.exists():
        print_case("FAIL", f"Missing manifest: {MANIFEST_PATH}")
        log_result("DT-17", "FAIL", {"returncode": 1}, notes=str(MANIFEST_PATH))
        return 1

    try:
        ready_ids, blocked_ids = _load_dataset_sets()
    except Exception as exc:
        print_case("FAIL", f"Could not parse dataset manifest: {exc}")
        log_result("DT-17", "FAIL", {"returncode": 1}, notes=str(exc))
        return 1

    repo_only_mode = os.getenv("ZPE_IOT_ALLOW_MISSING_RAW_ARTIFACTS") == "1"

    ready_args = ["--datasets", *ready_ids]
    if repo_only_mode:
        ready_args.insert(0, "--allow-missing-raw")
    ready_proc = _verify(*ready_args)
    ready_out = (ready_proc.stdout + ready_proc.stderr).strip()
    if ready_out:
        print(ready_out)
    if ready_proc.returncode != 0:
        print_case("FAIL", "READY dataset provenance verification failed")
        log_result("DT-17", "FAIL", {"returncode": ready_proc.returncode}, notes=ready_out[-1000:])
        return 1

    blocked_declared: list[str] = []
    if blocked_ids:
        blocked_args = ["--allow-blocked", "--datasets", *blocked_ids]
        if repo_only_mode:
            blocked_args.insert(1, "--allow-missing-raw")
        blocked_proc = _verify(*blocked_args)
        blocked_out = (blocked_proc.stdout + blocked_proc.stderr).strip()
        if blocked_proc.returncode != 0 or "[BLOCKED]" not in blocked_out:
            print_case("FAIL", "BLOCKED dataset declaration integrity failed")
            log_result("DT-17", "FAIL", {"returncode": blocked_proc.returncode}, notes=blocked_out[-1000:])
            return 1
        blocked_declared = blocked_ids

    if blocked_declared:
        print(f"Blocked datasets remain explicitly declared: {', '.join(blocked_declared)}")

    pass_message = "READY datasets verified and BLOCKED datasets remain explicitly declared"
    if repo_only_mode:
        pass_message += " (repo-only mode; raw dataset mirror gated behind ZPE_IOT_ALLOW_MISSING_RAW_ARTIFACTS=1)"

    print_case("PASS", pass_message)
    log_result("DT-17", "PASS", {"returncode": 0, "repo_only_mode": repo_only_mode})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
