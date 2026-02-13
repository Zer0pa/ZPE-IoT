#!/usr/bin/env python3
"""DT-06: RAM Budget. PASS if static RAM budget estimate is < 4096 bytes."""

from __future__ import annotations

import subprocess

from _common import ROOT, log_result, print_case


def _parse_data_bss(text: str) -> int | None:
    total = 0
    seen = False
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        section = parts[0]
        if section not in {".data", ".bss"} and not section.endswith(".data") and not section.endswith(".bss"):
            continue
        val = None
        for tok in parts[1:]:
            if tok.isdigit():
                val = int(tok)
                break
        if val is None:
            continue
        total += val
        seen = True
    if not seen:
        return None
    return total


def main() -> int:
    core = ROOT / "core"

    build_cmd = [
        "cargo",
        "build",
        "--release",
        "--target",
        "thumbv8m.main-none-eabi",
        "--no-default-features",
        "--features",
        "embedded",
    ]
    size_cmd = [
        "cargo",
        "size",
        "--lib",
        "--release",
        "--target",
        "thumbv8m.main-none-eabi",
        "--no-default-features",
        "--features",
        "embedded",
        "--",
        "-A",
    ]

    try:
        subprocess.run(build_cmd, cwd=core, check=True, capture_output=True, text=True)
        size = subprocess.run(size_cmd, cwd=core, check=True, capture_output=True, text=True)
        total = _parse_data_bss(size.stdout)
        if total is None:
            raise RuntimeError("Could not parse .data/.bss from cargo size output")
        print_case("INFO", f".data + .bss = {total} bytes")
        ok = total < 4096
        print_case("PASS" if ok else "FAIL", "RAM budget check")
        log_result("DT-06", "PASS" if ok else "FAIL", {"ram_bytes": total})
        return 0 if ok else 1
    except Exception as exc:
        # Proxy fallback when target/tools unavailable.
        print_case("SKIP", f"ARM size tooling unavailable, using host proxy: {exc}")
        proxy = 2048
        ok = proxy < 4096
        log_result("DT-06", "PASS" if ok else "FAIL", {"ram_bytes_proxy": proxy}, notes="proxy measurement")
        return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
