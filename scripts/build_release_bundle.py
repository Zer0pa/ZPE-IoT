#!/usr/bin/env python3
"""Assemble a local release-candidate bundle (publish deferred)."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "validation" / "results"
RELEASE_ROOT = ROOT / "release"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _latest(pattern: str) -> Path | None:
    files = sorted(RESULTS_DIR.glob(pattern))
    return files[-1] if files else None


def _copy(src: Path, dst_root: Path, target_rel: str) -> Path:
    dst = dst_root / target_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def main() -> int:
    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    rc_dir = RELEASE_ROOT / f"RC_{ts}"
    rc_dir.mkdir(parents=True, exist_ok=True)

    copied: list[Path] = []

    # Python package artifacts
    for artifact in sorted((ROOT / "python" / "dist").glob("zpe_iot-*.whl")):
        copied.append(_copy(artifact, rc_dir, f"python_dist/{artifact.name}"))
    for artifact in sorted((ROOT / "python" / "dist").glob("zpe_iot-*.tar.gz")):
        copied.append(_copy(artifact, rc_dir, f"python_dist/{artifact.name}"))

    # Core benchmark + gate artifacts
    patterns = [
        "bench_summary_[0-9]*.json",
        "bench_summary_E0_proxy_*.json",
        "bench_summary_E1_real_public_*.json",
        "bench_summary_E2_real_customer_*.json",
        "bench_vs_zstd_*.json",
        "bench_vs_lz4_*.json",
        "bench_vs_zlib_*.json",
        "bench_vs_gorilla_*.json",
        "dt_results_*.json",
        "wi1_ablation_*.json",
        "zh1_ablation_*.json",
        "perf_profile_hot_paths_*.json",
        "vulnerability_scan_*.json",
        "vulnerability_scan_*.sha256",
        "sbom_[0-9]*.json",
        "sbom_python_*.json",
        "sbom_rust_*.json",
        "license_manifest_*.json",
        "release_manifest_*.json",
        "release_checksums_*.txt",
        "iot_wave1_phase2_checksums.txt",
    ]
    for pattern in patterns:
        latest = _latest(pattern)
        if latest is not None:
            copied.append(_copy(latest, rc_dir, f"validation_results/{latest.name}"))

    coverage_xml = RESULTS_DIR / "coverage" / "python_coverage.xml"
    if coverage_xml.exists():
        copied.append(_copy(coverage_xml, rc_dir, "validation_results/coverage/python_coverage.xml"))

    # Documentation bundle
    doc_files = [
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "SECURITY.md",
        ROOT / "SUPPORT.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "docs" / "BENCHMARKS.md",
        ROOT / "docs" / "FIDELITY_SEMANTICS.md",
        ROOT / "docs" / "ARCH_TIGHTNESS_AUDIT.md",
        ROOT / "docs" / "CI_POLICY.md",
        ROOT / "docs" / "CLI_CONTRACT.md",
        ROOT / "docs" / "TEST_MATRIX.md",
        ROOT / "docs" / "RELEASE_CHECKLIST.md",
        ROOT / "docs" / "ZPE_IOT_SALES_BRIEF.md",
        ROOT / "docs" / "OUTREACH_TEMPLATE.md",
    ]
    for doc in doc_files:
        if doc.exists():
            copied.append(_copy(doc, rc_dir, f"docs/{doc.name}"))

    # Memory snapshot from root governance docs (synced into project_docs)
    project_docs = ROOT / "project_docs"
    if project_docs.exists():
        for path in sorted(project_docs.rglob("*")):
            if path.is_file():
                rel = path.relative_to(project_docs)
                copied.append(_copy(path, rc_dir, f"project_docs/{rel}"))

    manifest = {
        "timestamp": ts,
        "bundle_path": str(rc_dir),
        "file_count": len(copied),
        "files": [
            {
                "path": str(path.relative_to(rc_dir)),
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in sorted(copied)
        ],
    }
    manifest_path = rc_dir / "bundle_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    hash_path = rc_dir / "bundle_manifest.sha256"
    hash_path.write_text(f"{_sha256(manifest_path)}  {manifest_path.name}\n", encoding="utf-8")

    print(f"Saved: {manifest_path}")
    print(f"Saved: {hash_path}")
    print(f"Bundle: {rc_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
