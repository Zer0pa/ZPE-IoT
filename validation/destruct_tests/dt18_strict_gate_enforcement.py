#!/usr/bin/env python3
"""DT-18: Strict Gate Enforcement. PASS if mandatory SKIP fails strict mode."""

from __future__ import annotations

import os
import subprocess
import sys

from _common import ROOT, log_result, print_case


def _run(strict: bool) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(ROOT / "validation" / "destruct_tests" / "run_all_dts.py"), "--dt", "6"]
    if strict:
        cmd.append("--strict-gates")
    else:
        cmd.append("--no-strict-gates")

    env = os.environ.copy()
    env["ZPE_IOT_FORCE_SKIP_DT06"] = "1"
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, env=env)


def main() -> int:
    strict = _run(strict=True)
    relaxed = _run(strict=False)

    strict_failed = strict.returncode != 0
    relaxed_passed = relaxed.returncode == 0

    if strict_failed and relaxed_passed:
        print_case("PASS", "Strict mode rejects mandatory SKIP while relaxed mode allows exploratory SKIP")
        log_result("DT-18", "PASS", {"strict_rc": strict.returncode, "relaxed_rc": relaxed.returncode})
        return 0

    if not strict_failed:
        print_case("FAIL", "Strict mode did not fail on forced mandatory SKIP")
    if not relaxed_passed:
        print_case("FAIL", "Relaxed mode unexpectedly failed on forced SKIP")

    notes = (
        "strict_stdout:\n"
        + strict.stdout[-600:]
        + "\nstrict_stderr:\n"
        + strict.stderr[-600:]
        + "\nrelaxed_stdout:\n"
        + relaxed.stdout[-600:]
        + "\nrelaxed_stderr:\n"
        + relaxed.stderr[-600:]
    )
    log_result("DT-18", "FAIL", {"strict_rc": strict.returncode, "relaxed_rc": relaxed.returncode}, notes=notes)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
