#!/usr/bin/env python3
"""Checklist-driven local release preflight with machine-readable reporting."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from runtime_surface import python_executable, tool_command

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "validation" / "results"
PYTHON_BIN = str(python_executable())
CLI_BIN = tool_command("zpe-iot")


REPORT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "IoT Release Preflight Report",
    "type": "object",
    "required": ["timestamp_utc", "summary", "checks"],
    "properties": {
        "timestamp_utc": {"type": "string"},
        "summary": {
            "type": "object",
            "required": ["total", "pass", "fail", "critical_failures"],
            "properties": {
                "total": {"type": "integer", "minimum": 0},
                "pass": {"type": "integer", "minimum": 0},
                "fail": {"type": "integer", "minimum": 0},
                "critical_failures": {"type": "integer", "minimum": 0},
            },
        },
        "checks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "description", "critical", "status", "started_utc", "ended_utc", "duration_s"],
                "properties": {
                    "id": {"type": "string"},
                    "description": {"type": "string"},
                    "critical": {"type": "boolean"},
                    "status": {"type": "string", "enum": ["PASS", "FAIL", "SKIPPED", "DEFERRED"]},
                    "started_utc": {"type": "string"},
                    "ended_utc": {"type": "string"},
                    "duration_s": {"type": "number"},
                    "command": {"type": "array", "items": {"type": "string"}},
                    "returncode": {"type": ["integer", "null"]},
                    "details": {"type": "string"},
                    "artifacts": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    },
}


@dataclass
class CmdResult:
    returncode: int
    output: str
    duration_s: float


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _latest(pattern: str, root: Path) -> Path | None:
    files = sorted(root.glob(pattern))
    return files[-1] if files else None


def _run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> CmdResult:
    start = time.perf_counter()
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    try:
        proc = subprocess.run(cmd, cwd=str(cwd or ROOT), capture_output=True, text=True, env=merged_env)
    except OSError as exc:
        end = time.perf_counter()
        return CmdResult(returncode=127, output=f"command launch failed: {exc}", duration_s=end - start)
    end = time.perf_counter()
    output = (proc.stdout or "") + (proc.stderr or "")
    return CmdResult(returncode=proc.returncode, output=output, duration_s=end - start)


def _python_rust_target() -> str | None:
    system = platform.system().lower()
    machine = platform.machine().lower()
    target_map = {
        ("darwin", "x86_64"): "x86_64-apple-darwin",
        ("darwin", "arm64"): "aarch64-apple-darwin",
        ("darwin", "aarch64"): "aarch64-apple-darwin",
        ("linux", "x86_64"): "x86_64-unknown-linux-gnu",
        ("linux", "aarch64"): "aarch64-unknown-linux-gnu",
        ("linux", "arm64"): "aarch64-unknown-linux-gnu",
    }
    return target_map.get((system, machine))


def _build_and_run_dt_command() -> list[str]:
    dt_cmd = [PYTHON_BIN, "validation/destruct_tests/run_all_dts.py", "--strict-gates"]
    target = _python_rust_target()
    if target is None:
        return dt_cmd
    build_cmd = ["cargo", "build", "--release", "--target", target]
    return [
        PYTHON_BIN,
        "-c",
        (
            "import subprocess,sys; "
            f"sys.exit(subprocess.run({build_cmd!r}, cwd={str(ROOT / 'core')!r}).returncode "
            f"or subprocess.run({dt_cmd!r}, cwd={str(ROOT)!r}).returncode)"
        ),
    ]


def _hash_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _record(
    checks: list[dict],
    *,
    check_id: str,
    description: str,
    critical: bool,
    status: str,
    started_utc: str,
    ended_utc: str,
    duration_s: float,
    command: list[str] | None = None,
    returncode: int | None = None,
    details: str = "",
    artifacts: list[str] | None = None,
) -> None:
    checks.append(
        {
            "id": check_id,
            "description": description,
            "critical": critical,
            "status": status,
            "started_utc": started_utc,
            "ended_utc": ended_utc,
            "duration_s": round(duration_s, 3),
            "command": command or [],
            "returncode": returncode,
            "details": details[-4000:],
            "artifacts": artifacts or [],
        }
    )


def _print_status(status: str, check_id: str, desc: str) -> None:
    print(f"[{status}] {check_id}: {desc}")


def _dt_gate_ok(path: Path) -> tuple[bool, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        return False, f"cannot parse DT artifact: {exc}"
    results = payload.get("results", [])
    mandatory = payload.get("mandatory_failures", [])
    strict = payload.get("strict_gates") is True
    ok = strict and isinstance(results, list) and len(results) == 27 and isinstance(mandatory, list) and len(mandatory) == 0
    return ok, f"strict={strict} results={len(results) if isinstance(results, list) else 'NA'} mandatory_failures={len(mandatory) if isinstance(mandatory, list) else 'NA'}"


def _fresh_env_smoke() -> tuple[bool, str, list[str]]:
    wheel = _latest("zpe_iot-*.whl", ROOT / "python" / "dist")
    if wheel is None:
        return False, "no wheel found in python/dist", []

    smoke_root = RESULTS_DIR / f"fresh_env_smoke_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
    smoke_root.mkdir(parents=True, exist_ok=True)
    smoke_log = smoke_root / "smoke.log"

    venv_dir = smoke_root / "venv"
    commands: list[list[str]] = [
        [PYTHON_BIN, "-m", "venv", str(venv_dir)],
        [str(venv_dir / "bin" / "pip"), "install", "--upgrade", "pip"],
        [str(venv_dir / "bin" / "pip"), "install", str(wheel)],
    ]

    input_csv = smoke_root / "input.csv"
    packet = smoke_root / "packet.zpk"
    out_csv = smoke_root / "restored.csv"

    input_csv.write_text(
        "index,value\n" + "\n".join(f"{i},{(i * 0.05):.8f}" for i in range(256)) + "\n",
        encoding="utf-8",
    )

    commands.extend(
        [
            [str(venv_dir / "bin" / "zpe-iot"), "compress", str(input_csv), "--preset", "generic", "--output", str(packet)],
            [str(venv_dir / "bin" / "zpe-iot"), "info", str(packet), "--json"],
            [str(venv_dir / "bin" / "zpe-iot"), "decompress", str(packet), "--output", str(out_csv)],
            [
                str(venv_dir / "bin" / "zpe-iot"),
                "benchmark",
                str(input_csv),
                "--compare",
                "zlib",
                "--preset",
                "generic",
            ],
            [str(venv_dir / "bin" / "zpe-iot"), "diagnostics", "--json"],
        ]
    )

    with smoke_log.open("w", encoding="utf-8") as log:
        for cmd in commands:
            log.write(f"$ {' '.join(cmd)}\n")
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
            if proc.stdout:
                log.write(proc.stdout)
            if proc.stderr:
                log.write(proc.stderr)
            log.write(f"[rc={proc.returncode}]\n\n")
            if proc.returncode != 0:
                return False, f"fresh env command failed: {' '.join(cmd)}", [str(smoke_log)]

    if not packet.exists() or not out_csv.exists():
        return False, "fresh env smoke did not produce expected packet/output files", [str(smoke_log)]

    return True, "fresh env command smoke passed", [str(smoke_log), str(packet), str(out_csv)]


def run_preflight(report_json: Path, schema_json: Path | None) -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    checks: list[dict] = []

    def run_check(
        *,
        check_id: str,
        description: str,
        critical: bool,
        cmd: list[str],
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        validator=None,
        artifacts: list[str] | None = None,
    ) -> bool:
        started = _now()
        result = _run(cmd, cwd=cwd, env=env)
        ended = _now()
        ok = result.returncode == 0
        details = result.output
        if validator is not None:
            v_ok, v_detail = validator(result)
            ok = ok and v_ok
            details = (details + "\n" + v_detail).strip()
        status = "PASS" if ok else "FAIL"
        _record(
            checks,
            check_id=check_id,
            description=description,
            critical=critical,
            status=status,
            started_utc=started,
            ended_utc=ended,
            duration_s=result.duration_s,
            command=cmd,
            returncode=result.returncode,
            details=details,
            artifacts=artifacts,
        )
        _print_status(status, check_id, description)
        return ok

    # 1) Core checklist gates
    run_check(
        check_id="C01_RUST_TEST",
        description="cargo test --release passes",
        critical=True,
        cmd=["cargo", "test", "--release"],
        cwd=ROOT / "core",
    )
    run_check(
        check_id="C02_RUST_CLIPPY",
        description="cargo clippy -- -D warnings passes",
        critical=True,
        cmd=["cargo", "clippy", "--", "-D", "warnings"],
        cwd=ROOT / "core",
    )
    run_check(
        check_id="C03_PYTEST",
        description="pytest -q passes with coverage >= 85%",
        critical=True,
        cmd=[PYTHON_BIN, "-m", "pytest", "-q"],
        cwd=ROOT / "python",
    )

    def _dt_validator(_: CmdResult) -> tuple[bool, str]:
        latest = _latest("dt_results_*.json", ROOT / "validation" / "results")
        if latest is None:
            return False, "no dt_results_*.json generated"
        ok, detail = _dt_gate_ok(latest)
        return ok, f"latest_dt={latest} {detail}"

    run_check(
        check_id="C04_STRICT_DT",
        description="strict DT run passes with mandatory SKIPPED=0",
        critical=True,
        cmd=_build_and_run_dt_command(),
        cwd=ROOT,
        validator=_dt_validator,
    )

    def _bench_split_validator(_: CmdResult) -> tuple[bool, str]:
        req = [
            _latest("bench_summary_E0_proxy_*.json", ROOT / "validation" / "results"),
            _latest("bench_summary_E1_real_public_*.json", ROOT / "validation" / "results"),
            _latest("bench_summary_E2_real_customer_*.json", ROOT / "validation" / "results"),
        ]
        ok = all(p is not None for p in req)
        return ok, "bench_split_artifacts=" + ", ".join(str(p) for p in req if p is not None)

    run_check(
        check_id="C05_BENCH_SPLIT",
        description="benchmark split artifacts (E0/E1/E2) regenerated",
        critical=True,
        cmd=[
            PYTHON_BIN,
            "-c",
            (
                "import subprocess,sys; "
                "sys.exit(subprocess.run([r'" + PYTHON_BIN + "', 'validation/benchmarks/run_benchmarks.py']).returncode "
                "or subprocess.run([r'" + PYTHON_BIN + "', 'validation/benchmarks/generate_report.py']).returncode)"
            ),
        ],
        cwd=ROOT,
        validator=_bench_split_validator,
    )

    def _security_validator(result: CmdResult) -> tuple[bool, str]:
        latest = _latest("vulnerability_scan_*.json", ROOT / "validation" / "results")
        if latest is None:
            return False, "no vulnerability_scan_*.json generated"
        payload = json.loads(latest.read_text(encoding="utf-8"))
        high = int(payload.get("summary", {}).get("high_or_critical_count", 9999))
        return high == 0 and result.returncode == 0, f"latest_scan={latest} high_or_critical={high}"

    run_check(
        check_id="C06_SECURITY_SCAN",
        description="security scan artifact generated with high/critical=0",
        critical=True,
        cmd=[PYTHON_BIN, "scripts/security_scan.py"],
        cwd=ROOT,
        validator=_security_validator,
    )

    def _sbom_validator(_: CmdResult) -> tuple[bool, str]:
        patterns = [
            "sbom_[0-9]*.json",
            "sbom_python_*.json",
            "sbom_rust_*.json",
            "license_manifest_*.json",
            "release_manifest_*.json",
        ]
        found = {pat: _latest(pat, ROOT / "validation" / "results") for pat in patterns}
        ok = all(path is not None for path in found.values())
        return ok, "artifacts=" + ", ".join(f"{k}:{v}" for k, v in found.items() if v is not None)

    run_check(
        check_id="C07_SBOM_RELEASE_MANIFEST",
        description="SBOM + license manifest + release manifest generated",
        critical=True,
        cmd=[PYTHON_BIN, "scripts/generate_release_artifacts.py"],
        cwd=ROOT,
        validator=_sbom_validator,
    )

    warning_re = re.compile(r"warning|deprecated|missing readme", flags=re.IGNORECASE)

    def _build_warning_validator(result: CmdResult) -> tuple[bool, str]:
        has_warning = bool(warning_re.search(result.output))
        return not has_warning and result.returncode == 0, "warnings_detected=" + str(has_warning)

    run_check(
        check_id="C08_PY_BUILD_WARNING_FREE",
        description="python -m build completes warning-free",
        critical=True,
        cmd=[PYTHON_BIN, "-m", "build"],
        cwd=ROOT / "python",
        validator=_build_warning_validator,
    )

    started = _now()
    t0 = time.perf_counter()
    smoke_ok, smoke_detail, smoke_artifacts = _fresh_env_smoke()
    ended = _now()
    _record(
        checks,
        check_id="C09_FRESH_VENV_SMOKE",
        description="fresh-venv install smoke (compress/info/decompress/benchmark/diagnostics)",
        critical=True,
        status="PASS" if smoke_ok else "FAIL",
        started_utc=started,
        ended_utc=ended,
        duration_s=time.perf_counter() - t0,
        details=smoke_detail,
        artifacts=smoke_artifacts,
    )
    _print_status("PASS" if smoke_ok else "FAIL", "C09_FRESH_VENV_SMOKE", "fresh environment command smoke")

    run_check(
        check_id="C10_CHEMOSENSE_CLI_SMOKE",
        description="chemosense CLI smoke passes (zpe-iot chemosense-smoke --json)",
        critical=True,
        cmd=[CLI_BIN, "chemosense-smoke", "--json"],
        cwd=ROOT,
    )
    run_check(
        check_id="C11_CHEMOSENSE_MODULE_SMOKE",
        description="chemosense module smoke passes (python -m zpe_iot.cli chemosense-smoke --json)",
        critical=True,
        cmd=[PYTHON_BIN, "-m", "zpe_iot.cli", "chemosense-smoke", "--json"],
        cwd=ROOT / "python",
    )
    run_check(
        check_id="C12_CHEMOSENSE_CONTRACT_TEST",
        description="chemosense contract tests pass",
        critical=True,
        cmd=[PYTHON_BIN, "-m", "pytest", "-q", "tests/test_chemosense_contract.py"],
        cwd=ROOT / "python",
        env={"PYTEST_ADDOPTS": "--no-cov"},
    )

    def _perf_validator(_: CmdResult) -> tuple[bool, str]:
        latest = _latest("perf_profile_chemosense_*.json", ROOT / "validation" / "results")
        return latest is not None, f"latest_perf={latest}"

    run_check(
        check_id="C13_CHEMOSENSE_PERF_PROFILE",
        description="chemosense perf profile artifact generated",
        critical=True,
        cmd=[PYTHON_BIN, "validation/benchmarks/profile_chemosense.py"],
        cwd=ROOT,
        validator=_perf_validator,
    )

    def _chemo_bench_validator(_: CmdResult) -> tuple[bool, str]:
        latest = _latest("bench_summary_chemosense_*.json", ROOT / "validation" / "results")
        return latest is not None, f"latest_bench={latest}"

    run_check(
        check_id="C14_CHEMOSENSE_BENCH_SUMMARY",
        description="chemosense benchmark summary artifact generated",
        critical=True,
        cmd=[PYTHON_BIN, "validation/benchmarks/run_chemosense_benchmarks.py"],
        cwd=ROOT,
        validator=_chemo_bench_validator,
    )
    run_check(
        check_id="C15_CHEMOSENSE_PROVENANCE",
        description="chemosense provenance manifest verified",
        critical=True,
        cmd=[PYTHON_BIN, "validation/datasets/verify_chemosense_provenance.py"],
        cwd=ROOT,
    )

    def _bundle_validator(_: CmdResult) -> tuple[bool, str]:
        latest_bundle = _latest("RC_[0-9]*", ROOT / "release")
        if latest_bundle is None:
            return False, "no release/RC_<timestamp> bundle found"
        manifest = latest_bundle / "bundle_manifest.json"
        sha = latest_bundle / "bundle_manifest.sha256"
        if not manifest.exists():
            return False, f"missing {manifest}"
        if not sha.exists():
            return False, f"missing {sha}"
        line = sha.read_text(encoding="utf-8").strip()
        ok = line.startswith(_hash_sha256(manifest))
        return ok, f"bundle={latest_bundle} manifest_sha_ok={ok}"

    run_check(
        check_id="C16_RELEASE_BUNDLE",
        description="release RC bundle + bundle manifest hash generated",
        critical=True,
        cmd=[PYTHON_BIN, "scripts/build_release_bundle.py"],
        cwd=ROOT,
        validator=_bundle_validator,
    )
    run_check(
        check_id="C17_MEMORY_DOC_SYNC",
        description="memory-doc snapshot synced into project_docs/",
        critical=True,
        cmd=["bash", "scripts/sync_memory_docs.sh"],
        cwd=ROOT,
    )

    # Deferred publish checks are non-critical and explicitly skipped.
    skipped_started = _now()
    _record(
        checks,
        check_id="D01_DEFERRED_PUBLISH",
        description="push tag / publish to PyPI / publish to crates.io / outreach execution",
        critical=False,
        status="DEFERRED",
        started_utc=skipped_started,
        ended_utc=_now(),
        duration_s=0.0,
        details="Deferred by policy; requires explicit user ratification.",
    )
    _print_status("DEFERRED", "D01_DEFERRED_PUBLISH", "external publishing steps")

    pass_count = sum(1 for c in checks if c["status"] == "PASS")
    fail_count = sum(1 for c in checks if c["status"] == "FAIL")
    critical_failures = sum(1 for c in checks if c["status"] == "FAIL" and c["critical"])

    report = {
        "timestamp_utc": _now(),
        "summary": {
            "total": len(checks),
            "pass": pass_count,
            "fail": fail_count,
            "critical_failures": critical_failures,
        },
        "checks": checks,
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Saved report: {report_json}")

    if schema_json is not None:
        schema_json.parent.mkdir(parents=True, exist_ok=True)
        schema_json.write_text(json.dumps(REPORT_SCHEMA, indent=2) + "\n", encoding="utf-8")
        print(f"Saved schema: {schema_json}")

    print(
        "Summary: "
        f"total={report['summary']['total']} pass={pass_count} fail={fail_count} critical_failures={critical_failures}"
    )
    return 0 if critical_failures == 0 else 1


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-json",
        type=Path,
        default=ROOT / "validation" / "results" / f"release_preflight_report_{ts}.json",
        help="Path to write machine-readable preflight report.",
    )
    parser.add_argument(
        "--schema-json",
        type=Path,
        default=None,
        help="Optional path to write report JSON schema.",
    )
    args = parser.parse_args()
    return run_preflight(report_json=args.report_json, schema_json=args.schema_json)


if __name__ == "__main__":
    raise SystemExit(main())
