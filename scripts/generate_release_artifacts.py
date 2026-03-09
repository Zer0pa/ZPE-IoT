#!/usr/bin/env python3
"""Generate SBOM, license manifest, and release manifest artifacts."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "validation" / "results"


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd or ROOT), capture_output=True, text=True, check=True)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _latest(pattern: str) -> Path | None:
    files = sorted(RESULTS_DIR.glob(pattern))
    return files[-1] if files else None


def _tool_output(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=str(ROOT), text=True, stderr=subprocess.STDOUT).strip()
    except Exception:
        return "unavailable"


def _collect_component_licenses(sbom: dict, ecosystem: str) -> list[dict]:
    out: list[dict] = []
    for comp in sbom.get("components", []):
        name = comp.get("name")
        version = comp.get("version")
        licenses = comp.get("licenses") or []
        if not licenses:
            out.append(
                {
                    "ecosystem": ecosystem,
                    "name": name,
                    "version": version,
                    "licenses": ["UNKNOWN"],
                }
            )
            continue

        values: list[str] = []
        for item in licenses:
            if not isinstance(item, dict):
                continue
            lic = item.get("license", {}) if isinstance(item.get("license"), dict) else {}
            values.append(str(lic.get("id") or lic.get("name") or "UNKNOWN"))
        out.append(
            {
                "ecosystem": ecosystem,
                "name": name,
                "version": version,
                "licenses": sorted(set(values)) if values else ["UNKNOWN"],
            }
        )
    return out


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

    py_sbom = RESULTS_DIR / f"sbom_python_{ts}.json"
    rust_sbom_tmp = ROOT / "core" / f"sbom_rust_{ts}.json"
    rust_sbom = RESULTS_DIR / f"sbom_rust_{ts}.json"
    combined_sbom = RESULTS_DIR / f"sbom_{ts}.json"

    cyclonedx_py = ROOT / ".venv" / "bin" / "cyclonedx-py"
    if not cyclonedx_py.exists():
        discovered = shutil.which("cyclonedx-py")
        if discovered:
            cyclonedx_py = Path(discovered)
        else:
            raise RuntimeError("cyclonedx-py not found in project venv or PATH")

    _run(
        [
            str(cyclonedx_py),
            "environment",
            str(ROOT / ".venv"),
            "--of",
            "JSON",
            "--output-reproducible",
            "--no-validate",
            "-o",
            str(py_sbom),
        ],
        cwd=ROOT,
    )

    _run(
        [
            "cargo",
            "cyclonedx",
            "--manifest-path",
            str(ROOT / "core" / "Cargo.toml"),
            "--format",
            "json",
            "--override-filename",
            f"sbom_rust_{ts}",
        ],
        cwd=ROOT,
    )
    if not rust_sbom_tmp.exists():
        raise RuntimeError("Rust SBOM was not generated")
    shutil.move(str(rust_sbom_tmp), str(rust_sbom))

    py_doc = json.loads(py_sbom.read_text(encoding="utf-8"))
    rust_doc = json.loads(rust_sbom.read_text(encoding="utf-8"))

    combined_payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_sbom": {
            "path": str(py_sbom),
            "sha256": _sha256(py_sbom),
            "component_count": len(py_doc.get("components", [])),
        },
        "rust_sbom": {
            "path": str(rust_sbom),
            "sha256": _sha256(rust_sbom),
            "component_count": len(rust_doc.get("components", [])),
        },
    }
    combined_sbom.write_text(json.dumps(combined_payload, indent=2) + "\n", encoding="utf-8")

    license_manifest = RESULTS_DIR / f"license_manifest_{ts}.json"
    license_rows = _collect_component_licenses(py_doc, ecosystem="python") + _collect_component_licenses(
        rust_doc,
        ecosystem="rust",
    )
    license_payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "component_count": len(license_rows),
        "components": sorted(license_rows, key=lambda x: (x["ecosystem"], x.get("name") or "")),
    }
    license_manifest.write_text(json.dumps(license_payload, indent=2) + "\n", encoding="utf-8")

    dt_latest = _latest("dt_results_*.json")
    bench_latest = _latest("bench_summary_[0-9]*.json")
    vuln_latest = _latest("vulnerability_scan_*.json")

    artifact_paths = [p for p in [dt_latest, bench_latest, vuln_latest, py_sbom, rust_sbom, combined_sbom, license_manifest] if p]
    artifact_hashes = {str(p): _sha256(p) for p in artifact_paths}

    git_sha = _tool_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"])
    python_version = _tool_output([str(ROOT / ".venv" / "bin" / "python"), "--version"])
    pip_version = _tool_output([str(ROOT / ".venv" / "bin" / "pip"), "--version"])
    cargo_version = _tool_output(["cargo", "--version"])
    rustc_version = _tool_output(["rustc", "-Vv"])

    toolchain_raw = {
        "python": python_version,
        "pip": pip_version,
        "cargo": cargo_version,
        "rustc": rustc_version,
    }
    toolchain_hashes = {
        k: hashlib.sha256(v.encode("utf-8")).hexdigest() for k, v in toolchain_raw.items()
    }

    release_manifest = RESULTS_DIR / f"release_manifest_{ts}.json"
    release_payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "commit_sha": git_sha,
        "build_toolchain": toolchain_raw,
        "build_toolchain_hashes": toolchain_hashes,
        "benchmark_artifacts": [str(p) for p in [bench_latest] if p],
        "dt_artifacts": [str(p) for p in [dt_latest] if p],
        "security_artifacts": [str(p) for p in [vuln_latest, combined_sbom, license_manifest] if p],
        "artifact_sha256": artifact_hashes,
    }
    release_manifest.write_text(json.dumps(release_payload, indent=2) + "\n", encoding="utf-8")

    print(f"Saved: {combined_sbom}")
    print(f"Saved: {license_manifest}")
    print(f"Saved: {release_manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
