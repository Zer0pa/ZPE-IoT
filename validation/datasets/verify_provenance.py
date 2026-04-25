#!/usr/bin/env python3
"""Validate dataset provenance manifest and hash integrity for sensor datasets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT / "validation" / "datasets"
MANIFEST_PATH = DATASETS_DIR / "manifest.json"

READY_REQUIRED_FIELDS = [
    "provenance_class",
    "source_url",
    "license",
    "retrieval_date_utc",
    "raw_sha256",
    "transform_sha256",
    "notes",
]
BLOCKED_REQUIRED_FIELDS = [
    "provenance_class",
    "source_url",
    "license",
    "notes",
    "blocked_reason",
]
CLASS_ORDER = {"proxy": 0, "real_public": 1, "real_customer": 2}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_iso_utc(ts: str) -> bool:
    try:
        if ts.endswith("Z"):
            datetime.fromisoformat(ts[:-1] + "+00:00")
        else:
            datetime.fromisoformat(ts)
        return True
    except Exception:
        return False


def _validate_entry(
    ds_id: str,
    entry: dict,
    min_class: str,
    allow_blocked: bool,
    allow_missing_raw: bool,
) -> tuple[str, list[str]]:
    issues: list[str] = []
    notes: list[str] = []
    status = str(entry.get("status", "READY")).upper()

    required_fields = BLOCKED_REQUIRED_FIELDS if status == "BLOCKED" else READY_REQUIRED_FIELDS
    for field in required_fields:
        if field not in entry:
            issues.append(f"missing field `{field}`")

    if issues:
        return "FAIL", issues

    prov_class = str(entry["provenance_class"])
    if prov_class not in CLASS_ORDER:
        issues.append(f"invalid provenance_class `{prov_class}`")
        return "FAIL", issues

    if status not in {"READY", "BLOCKED"}:
        issues.append(f"invalid status `{status}`")

    source_url = str(entry["source_url"]).strip()
    if not source_url.startswith(("http://", "https://")):
        issues.append("source_url must be http(s)")

    if status == "BLOCKED":
        blocked_reason = str(entry.get("blocked_reason", "")).strip()
        if not blocked_reason:
            issues.append("status=BLOCKED requires blocked_reason")
        if not allow_blocked:
            issues.append("blocked dataset not allowed in strict verification")
        if allow_blocked and not issues:
            return "BLOCKED", [blocked_reason]
    else:
        retrieval_date_utc = str(entry["retrieval_date_utc"]).strip()
        if not _is_iso_utc(retrieval_date_utc):
            issues.append("retrieval_date_utc must be ISO8601")

        raw_sha = str(entry["raw_sha256"]).strip().lower()
        tf_sha = str(entry["transform_sha256"]).strip().lower()
        if len(raw_sha) != 64 or any(c not in "0123456789abcdef" for c in raw_sha):
            issues.append("raw_sha256 must be a 64-char hex SHA256")
        if len(tf_sha) != 64 or any(c not in "0123456789abcdef" for c in tf_sha):
            issues.append("transform_sha256 must be a 64-char hex SHA256")

        ds_dir = DATASETS_DIR / ds_id
        transform_path = ds_dir / "data.npz"
        raw_rel = str(entry.get("raw_artifact", "")).strip()
        raw_path = (ROOT / raw_rel) if raw_rel else None

        if not transform_path.exists():
            issues.append(f"missing transformed artifact `{transform_path}`")
        else:
            actual_tf_sha = _sha256(transform_path)
            if actual_tf_sha != tf_sha:
                issues.append("transform_sha256 mismatch")

        if raw_path is None:
            issues.append("missing `raw_artifact` path")
        elif not raw_path.exists():
            if allow_missing_raw:
                notes.append(f"raw artifact unavailable in repo-only mode: `{raw_path}`")
            else:
                issues.append(f"missing raw artifact `{raw_path}`")
        else:
            actual_raw_sha = _sha256(raw_path)
            if actual_raw_sha != raw_sha:
                issues.append("raw_sha256 mismatch")

    min_rank = CLASS_ORDER[min_class]
    if CLASS_ORDER[prov_class] < min_rank:
        issues.append(f"provenance_class `{prov_class}` is below required `{min_class}`")

    if issues:
        if status == "BLOCKED" and allow_blocked:
            return "BLOCKED", issues
        return "FAIL", issues
    return "PASS", notes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-class", choices=sorted(CLASS_ORDER), default="real_public")
    parser.add_argument("--allow-blocked", action="store_true")
    parser.add_argument("--allow-missing-raw", action="store_true")
    parser.add_argument("--datasets", nargs="*", default=None)
    args = parser.parse_args()

    allow_missing_raw = args.allow_missing_raw or os.getenv("ZPE_IOT_ALLOW_MISSING_RAW_ARTIFACTS") == "1"

    if not MANIFEST_PATH.exists():
        print(f"[FAIL] missing manifest: {MANIFEST_PATH}")
        return 1

    try:
        manifest = json.loads(MANIFEST_PATH.read_text())
    except Exception as exc:
        print(f"[FAIL] invalid JSON manifest: {exc}")
        return 1

    dataset_ids = args.datasets or sorted(
        (ds_id for ds_id in manifest if ds_id.startswith("DS-")),
        key=lambda ds_id: int(ds_id.split("-")[1]),
    )

    overall_ok = True
    blocked_count = 0
    for ds_id in dataset_ids:
        entry = manifest.get(ds_id)
        if not isinstance(entry, dict):
            print(f"[FAIL] {ds_id}: missing manifest entry")
            overall_ok = False
            continue

        status, issues = _validate_entry(
            ds_id,
            entry,
            args.min_class,
            args.allow_blocked,
            allow_missing_raw,
        )
        if status == "PASS":
            detail = f" ({entry['provenance_class']})"
            if issues:
                detail += "; " + "; ".join(issues)
            print(f"[PASS] {ds_id}: provenance + hashes verified{detail}")
            continue
        if status == "BLOCKED":
            blocked_count += 1
            print(f"[BLOCKED] {ds_id}: " + "; ".join(issues))
            continue
        overall_ok = False
        print(f"[FAIL] {ds_id}: " + "; ".join(issues))

    if overall_ok and blocked_count == 0:
        return 0
    if overall_ok and blocked_count > 0 and args.allow_blocked:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
