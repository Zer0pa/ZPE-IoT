#!/usr/bin/env python3
"""Generate SHA-256 checksums for latest release-relevant artifacts."""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "validation" / "results"
RELEASE_DIR = ROOT / "release"
DIST_DIR = ROOT / "python" / "dist"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _latest(pattern: str, root: Path) -> Path | None:
    files = sorted(root.glob(pattern))
    return files[-1] if files else None


def _collect_latest() -> list[Path]:
    patterns = [
        ("zpe_iot-*.whl", DIST_DIR),
        ("zpe_iot-*.tar.gz", DIST_DIR),
        ("dt_results_*.json", RESULTS_DIR),
        ("bench_summary_[0-9]*.json", RESULTS_DIR),
        ("bench_summary_E0_proxy_*.json", RESULTS_DIR),
        ("bench_summary_E1_real_public_*.json", RESULTS_DIR),
        ("bench_summary_E2_real_customer_*.json", RESULTS_DIR),
        ("bench_summary_chemosense_*.json", RESULTS_DIR),
        ("perf_profile_chemosense_*.json", RESULTS_DIR),
        ("vulnerability_scan_*.json", RESULTS_DIR),
        ("sbom_[0-9]*.json", RESULTS_DIR),
        ("sbom_python_*.json", RESULTS_DIR),
        ("sbom_rust_*.json", RESULTS_DIR),
        ("license_manifest_*.json", RESULTS_DIR),
        ("release_manifest_*.json", RESULTS_DIR),
    ]

    selected: list[Path] = []
    for pattern, root in patterns:
        p = _latest(pattern, root)
        if p is not None:
            selected.append(p)

    rc_latest = _latest("RC_[0-9]*", RELEASE_DIR)
    if rc_latest is not None:
        manifest = rc_latest / "bundle_manifest.json"
        manifest_hash = rc_latest / "bundle_manifest.sha256"
        if manifest.exists():
            selected.append(manifest)
        if manifest_hash.exists():
            selected.append(manifest_hash)

    # deterministic order for stable diffs
    return sorted(set(selected))


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS_DIR / f"release_checksums_{ts}.txt",
    )
    args = parser.parse_args()

    artifacts = _collect_latest()
    if not artifacts:
        print("No release artifacts found for checksum generation")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        f.write(f"# checksum_generated_utc={datetime.now(timezone.utc).isoformat()}\n")
        for path in artifacts:
            rel = path.relative_to(ROOT)
            f.write(f"{_sha256(path)}  {rel}\n")

    print(f"Saved: {args.output}")
    print(f"Artifacts hashed: {len(artifacts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
