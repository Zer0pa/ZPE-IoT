#!/usr/bin/env python3
"""Pin a benchmark summary as immutable DT-16 baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "validation" / "results"
BASELINE_ROOT = RESULTS / "baseline"
ACTIVE_TAG_FILE = BASELINE_ROOT / "ACTIVE_BASELINE_TAG"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _latest_bench_summary() -> Path:
    files = sorted(RESULTS.glob("bench_summary_[0-9]*.json"))
    if not files:
        raise RuntimeError("No bench_summary artifacts found")
    return files[-1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-tag", required=True, help="Immutable baseline identity, e.g. draconian_20260214C")
    parser.add_argument("--source-summary", default=None, help="Path to bench_summary_*.json (defaults to latest)")
    parser.add_argument("--set-active", action="store_true", help="Write ACTIVE_BASELINE_TAG pointer")
    args = parser.parse_args()

    source = Path(args.source_summary).resolve() if args.source_summary else _latest_bench_summary()
    if not source.exists():
        raise RuntimeError(f"Source summary does not exist: {source}")

    BASELINE_ROOT.mkdir(parents=True, exist_ok=True)
    tag_dir = BASELINE_ROOT / args.baseline_tag
    tag_dir.mkdir(parents=True, exist_ok=True)

    pinned_summary = tag_dir / "bench_summary.json"
    shutil.copy2(source, pinned_summary)

    manifest_payload = {
        "manifest_version": 1,
        "baseline_tag": args.baseline_tag,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_summary_path": str(source),
        "bench_summary_path": str(pinned_summary),
        "bench_summary_sha256": _sha256(pinned_summary),
        "dataset_manifest_path": str(ROOT / "validation" / "datasets" / "manifest.json"),
        "dataset_manifest_sha256": _sha256(ROOT / "validation" / "datasets" / "manifest.json"),
        "creation_command": (
            "python validation/benchmarks/pin_baseline.py "
            f"--baseline-tag {args.baseline_tag} --source-summary {source}"
            + (" --set-active" if args.set_active else "")
        ),
    }
    manifest_path = tag_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest_payload, indent=2) + "\n")

    if args.set_active:
        ACTIVE_TAG_FILE.write_text(args.baseline_tag + "\n", encoding="utf-8")

    print(f"Pinned baseline: {pinned_summary}")
    print(f"Manifest: {manifest_path}")
    if args.set_active:
        print(f"Active tag pointer: {ACTIVE_TAG_FILE} -> {args.baseline_tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
