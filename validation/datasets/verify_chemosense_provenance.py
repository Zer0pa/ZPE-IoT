#!/usr/bin/env python3
"""Verify chemosense dataset provenance manifest and artifact hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "validation" / "datasets" / "manifest_chemosense.json"

CLASS_ORDER = {
    "E0": 0,
    "E1": 1,
    "E2": 2,
}

REQUIRED_FIELDS = {
    "status",
    "name",
    "provenance_class",
    "evidence_class",
    "source_url",
    "license",
    "retrieval_date_utc",
    "raw_artifact",
    "raw_sha256",
    "transform_artifact",
    "transform_sha256",
    "notes",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _has_min_class(actual: str, minimum: str) -> bool:
    if actual not in CLASS_ORDER or minimum not in CLASS_ORDER:
        return False
    return CLASS_ORDER[actual] >= CLASS_ORDER[minimum]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-class", default="E1", choices=["E0", "E1", "E2"])
    args = parser.parse_args()

    if not MANIFEST_PATH.exists():
        print("[FAIL] Missing chemosense manifest")
        return 1

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    required_ids = ["CS-01", "CS-02", "CS-03"]

    blocked = []
    errors = []

    for ds_id in required_ids:
        entry = manifest.get(ds_id)
        if not isinstance(entry, dict):
            errors.append(f"{ds_id}: missing manifest entry")
            continue

        status = str(entry.get("status", "")).upper()
        if status == "BLOCKED":
            blocked.append(ds_id)
            continue

        missing = sorted(REQUIRED_FIELDS - set(entry.keys()))
        if missing:
            errors.append(f"{ds_id}: missing fields {missing}")
            continue

        evidence_class = str(entry.get("evidence_class", ""))
        if not _has_min_class(evidence_class, args.min_class):
            errors.append(f"{ds_id}: evidence_class {evidence_class} below {args.min_class}")

        raw_path = ROOT / str(entry["raw_artifact"])
        transform_path = ROOT / str(entry["transform_artifact"])
        if not raw_path.exists():
            errors.append(f"{ds_id}: missing raw artifact {raw_path}")
            continue
        if not transform_path.exists():
            errors.append(f"{ds_id}: missing transform artifact {transform_path}")
            continue

        raw_sha = _sha256(raw_path)
        transform_sha = _sha256(transform_path)
        if raw_sha != str(entry.get("raw_sha256")):
            errors.append(f"{ds_id}: raw_sha256 mismatch")
        if transform_sha != str(entry.get("transform_sha256")):
            errors.append(f"{ds_id}: transform_sha256 mismatch")

        print(f"[PASS] {ds_id}: provenance + hashes verified ({evidence_class})")

    if blocked:
        print(f"[BLOCKED] blocked datasets: {', '.join(blocked)}")
        return 0

    if errors:
        for err in errors:
            print(f"[FAIL] {err}")
        return 1

    print(f"[PASS] CS-01..CS-03 provenance manifest verified (min class {args.min_class})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
