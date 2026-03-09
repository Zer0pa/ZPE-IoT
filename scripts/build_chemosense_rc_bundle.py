#!/usr/bin/env python3
"""Assemble a chemosense-focused release-candidate bundle (publish deferred)."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "validation" / "results"
RELEASE_ROOT = ROOT / "release"
STRICT_DT_REQUIRED_COUNT = 27


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _latest(pattern: str) -> Path | None:
    files = sorted(RESULTS_DIR.glob(pattern))
    return files[-1] if files else None


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _strict_dt_issues(payload: dict) -> list[str]:
    issues: list[str] = []
    if payload.get("strict_gates") is not True:
        issues.append("strict_gates!=true")

    results = payload.get("results")
    if not isinstance(results, list):
        issues.append("results_missing")
    elif len(results) != STRICT_DT_REQUIRED_COUNT:
        issues.append(f"results_count={len(results)} expected={STRICT_DT_REQUIRED_COUNT}")

    failures = payload.get("mandatory_failures")
    if not isinstance(failures, list):
        issues.append("mandatory_failures_missing")
    elif failures:
        issues.append(f"mandatory_failures={len(failures)}")
    return issues


def _latest_full_strict_dt() -> tuple[Path, dict]:
    candidates = sorted(RESULTS_DIR.glob("dt_results_*.json"), reverse=True)
    for path in candidates:
        try:
            payload = _load_json(path)
        except Exception:
            continue
        if not _strict_dt_issues(payload):
            return path, payload

    details = []
    for path in candidates[:8]:
        try:
            payload = _load_json(path)
            details.append(f"{path.name}: {', '.join(_strict_dt_issues(payload)) or 'OK'}")
        except Exception as exc:
            details.append(f"{path.name}: unreadable ({exc})")
    detail_text = "; ".join(details) if details else "no dt_results_*.json files found"
    raise RuntimeError(
        "No full strict DT artifact found "
        f"(requires strict_gates=true, results_count={STRICT_DT_REQUIRED_COUNT}, mandatory_failures empty). "
        f"Observed: {detail_text}"
    )


def _copy(src: Path, dst_root: Path, target_rel: str) -> Path:
    dst = dst_root / target_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def main() -> int:
    try:
        strict_dt_src, strict_dt_payload = _latest_full_strict_dt()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1

    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    rc_dir = RELEASE_ROOT / f"RC_CHEMOSENSE_{ts}"
    rc_dir.mkdir(parents=True, exist_ok=True)

    copied: list[Path] = []

    copied.append(_copy(strict_dt_src, rc_dir, f"validation_results/{strict_dt_src.name}"))

    # Core gate + benchmark artifacts
    patterns = [
        "bench_summary_[0-9]*.json",
        "bench_summary_E0_proxy_*.json",
        "bench_summary_E1_real_public_*.json",
        "bench_summary_E2_real_customer_*.json",
        "bench_summary_chemosense_*.json",
        "perf_profile_chemosense_*.json",
        "perf_profile_hot_paths_*.json",
        "wi1_ablation_*.json",
        "zh1_ablation_*.json",
        "release_manifest_*.json",
        "license_manifest_*.json",
        "sbom_[0-9]*.json",
        "sbom_python_*.json",
        "sbom_rust_*.json",
    ]
    for pattern in patterns:
        latest = _latest(pattern)
        if latest is not None:
            copied.append(_copy(latest, rc_dir, f"validation_results/{latest.name}"))

    # Chemo provenance artifacts
    chemo_manifest = ROOT / "validation" / "datasets" / "manifest_chemosense.json"
    if chemo_manifest.exists():
        copied.append(_copy(chemo_manifest, rc_dir, "validation_datasets/manifest_chemosense.json"))

    chemo_raw = ROOT / "validation" / "datasets" / "raw" / "chemosense"
    if chemo_raw.exists():
        for path in sorted(chemo_raw.glob("*")):
            if path.is_file():
                copied.append(_copy(path, rc_dir, f"validation_datasets/raw_chemosense/{path.name}"))

    # Documentation bundle
    doc_files = [
        ROOT / "README.md",
        ROOT / "docs" / "BENCHMARKS.md",
        ROOT / "docs" / "CHEMOSENSE_EXTENSION.md",
        ROOT / "docs" / "ARCH_TIGHTNESS_AUDIT.md",
        ROOT / "docs" / "CLI_CONTRACT.md",
        ROOT / "docs" / "RELEASE_CHECKLIST.md",
        ROOT / "docs" / "ZPE_IOT_SALES_BRIEF.md",
        ROOT / "docs" / "OUTREACH_TEMPLATE.md",
    ]
    for doc in doc_files:
        if doc.exists():
            copied.append(_copy(doc, rc_dir, f"docs/{doc.name}"))

    perf_docs = ROOT / "docs" / "perf"
    if perf_docs.exists():
        for path in sorted(perf_docs.glob("chemosense_profile_*.md")):
            copied.append(_copy(path, rc_dir, f"docs/perf/{path.name}"))

    manifest = {
        "timestamp": ts,
        "bundle_path": str(rc_dir),
        "file_count": len(copied),
        "strict_dt_evidence": {
            "source": str(strict_dt_src),
            "strict_gates": strict_dt_payload.get("strict_gates"),
            "results_count": len(strict_dt_payload.get("results", []))
            if isinstance(strict_dt_payload.get("results"), list)
            else None,
            "mandatory_failures": len(strict_dt_payload.get("mandatory_failures", []))
            if isinstance(strict_dt_payload.get("mandatory_failures"), list)
            else None,
        },
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

    print(f"Saved: {manifest_path}")
    print(f"Bundle: {rc_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
