#!/usr/bin/env python3
"""Build chemosense proxy dataset extracts with provenance metadata."""

from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT / "validation" / "datasets"
CHEMO_DIR = DATASETS_DIR / "raw" / "chemosense"
MANIFEST_PATH = DATASETS_DIR / "manifest_chemosense.json"

DS01_RAW = DATASETS_DIR / "raw" / "DS-01" / "AirQualityUCI.zip"
CS02_SOURCE_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
CS02_RAW = CHEMO_DIR / "CS-02_winequality_red_raw.csv"

CS01_EXTRACT = CHEMO_DIR / "CS-01_smell_airquality_extract.csv"
CS02_EXTRACT = CHEMO_DIR / "CS-02_taste_wine_extract.csv"
CS03_RAW = CHEMO_DIR / "CS-03_fusion_proxy_raw.csv"
CS03_TRANSFORM = CHEMO_DIR / "CS-03_fusion_proxy.jsonl"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _to_float(cell: str) -> float | None:
    value = cell.strip().replace(",", ".")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _build_cs01_extract(limit: int = 1024) -> int:
    rows_written = 0
    with zipfile.ZipFile(DS01_RAW, "r") as zf:
        names = {name.lower(): name for name in zf.namelist()}
        target = names.get("airqualityuci.csv")
        if target is None:
            raise RuntimeError("AirQualityUCI.csv missing in DS-01 zip")

        with zf.open(target, "r") as f_in, CS01_EXTRACT.open("w", newline="", encoding="utf-8") as f_out:
            reader = csv.reader((line.decode("utf-8", errors="ignore") for line in f_in), delimiter=";")
            writer = csv.writer(f_out)
            writer.writerow(
                [
                    "datetime",
                    "co_gt",
                    "pt08_s1_co",
                    "pt08_s2_nmhc",
                    "pt08_s3_nox",
                    "pt08_s4_no2",
                    "pt08_s5_o3",
                    "temperature",
                    "relative_humidity",
                ]
            )

            header = next(reader, None)
            if header is None:
                raise RuntimeError("AirQualityUCI.csv empty")

            for row in reader:
                if len(row) < 14:
                    continue
                if rows_written >= limit:
                    break

                date = row[0].strip()
                time = row[1].strip()
                values = [
                    _to_float(row[2]),
                    _to_float(row[4]),
                    _to_float(row[5]),
                    _to_float(row[6]),
                    _to_float(row[7]),
                    _to_float(row[8]),
                    _to_float(row[9]),
                    _to_float(row[10]),
                ]
                if any(v is None for v in values):
                    continue
                if any(v == -200.0 for v in values):
                    continue

                writer.writerow([f"{date} {time}", *[f"{v:.6f}" for v in values]])
                rows_written += 1

    return rows_written


def _download_cs02_raw() -> None:
    if CS02_RAW.exists() and CS02_RAW.stat().st_size > 0:
        return
    req = urllib.request.Request(CS02_SOURCE_URL, headers={"User-Agent": "zpe-iot-chemosense-builder/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 - fixed trusted source URL
        data = resp.read()
    CS02_RAW.write_bytes(data)


def _build_cs02_extract(limit: int = 1024) -> int:
    rows_written = 0
    with CS02_RAW.open("r", newline="", encoding="utf-8") as f_in, CS02_EXTRACT.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f_out:
        reader = csv.DictReader(f_in, delimiter=";")
        writer = csv.writer(f_out)
        writer.writerow(
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "chlorides",
                "residual_sugar",
                "quality",
            ]
        )

        for row in reader:
            if rows_written >= limit:
                break
            try:
                sample = [
                    float(row["fixed acidity"]),
                    float(row["volatile acidity"]),
                    float(row["citric acid"]),
                    float(row["chlorides"]),
                    float(row["residual sugar"]),
                    float(row["quality"]),
                ]
            except (KeyError, TypeError, ValueError):
                continue
            writer.writerow([f"{v:.6f}" for v in sample])
            rows_written += 1

    return rows_written


def _build_cs03_fusion_proxy(limit: int = 1024) -> int:
    rows_written = 0
    with CS01_EXTRACT.open("r", newline="", encoding="utf-8") as f_smell, CS02_EXTRACT.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as f_taste, CS03_RAW.open("w", newline="", encoding="utf-8") as f_raw, CS03_TRANSFORM.open(
        "w",
        encoding="utf-8",
    ) as f_jsonl:
        smell_reader = csv.DictReader(f_smell)
        taste_reader = csv.DictReader(f_taste)
        raw_writer = csv.writer(f_raw)
        raw_writer.writerow(
            [
                "frame_index",
                "smell_co_gt",
                "smell_s1",
                "smell_s2",
                "smell_s3",
                "taste_fixed_acidity",
                "taste_volatile_acidity",
                "taste_quality",
            ]
        )

        for idx, (smell_row, taste_row) in enumerate(zip(smell_reader, taste_reader)):
            if rows_written >= limit:
                break
            raw_writer.writerow(
                [
                    idx,
                    smell_row["co_gt"],
                    smell_row["pt08_s1_co"],
                    smell_row["pt08_s2_nmhc"],
                    smell_row["pt08_s3_nox"],
                    taste_row["fixed_acidity"],
                    taste_row["volatile_acidity"],
                    taste_row["quality"],
                ]
            )
            event = {
                "frame_index": idx,
                "smell_vector": [
                    float(smell_row["co_gt"]),
                    float(smell_row["pt08_s1_co"]),
                    float(smell_row["pt08_s2_nmhc"]),
                    float(smell_row["pt08_s3_nox"]),
                ],
                "taste_vector": [
                    float(taste_row["fixed_acidity"]),
                    float(taste_row["volatile_acidity"]),
                    float(taste_row["citric_acid"]),
                    float(taste_row["chlorides"]),
                    float(taste_row["residual_sugar"]),
                    float(taste_row["quality"]),
                ],
                "touch_proxy": {
                    "frame_tick": idx,
                    "pulse": int((idx * 7) % 256),
                },
            }
            f_jsonl.write(json.dumps(event, sort_keys=True) + "\n")
            rows_written += 1

    return rows_written


def main() -> int:
    CHEMO_DIR.mkdir(parents=True, exist_ok=True)
    if not DS01_RAW.exists():
        raise RuntimeError(f"Missing DS-01 raw artifact: {DS01_RAW}")

    cs01_count = _build_cs01_extract(limit=1024)
    _download_cs02_raw()
    cs02_count = _build_cs02_extract(limit=1024)
    cs03_count = _build_cs03_fusion_proxy(limit=min(cs01_count, cs02_count))

    now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    manifest = {
        "CS-01": {
            "status": "READY",
            "name": "AirQualityUCI gas-channel smell proxy extract",
            "provenance_class": "real_public",
            "evidence_class": "E1",
            "source_url": "https://archive.ics.uci.edu/ml/machine-learning-databases/00360/AirQualityUCI.zip",
            "license": "CC BY 4.0 (UCI repository terms)",
            "retrieval_date_utc": now_utc,
            "raw_artifact": str(DS01_RAW.relative_to(ROOT)),
            "raw_sha256": _sha256(DS01_RAW),
            "transform_artifact": str(CS01_EXTRACT.relative_to(ROOT)),
            "transform_sha256": _sha256(CS01_EXTRACT),
            "rows": cs01_count,
            "notes": "Filtered valid gas-sensor rows from AirQualityUCI.csv; removed sentinel -200 values.",
        },
        "CS-02": {
            "status": "READY",
            "name": "Wine Quality red-chemistry taste proxy extract",
            "provenance_class": "real_public",
            "evidence_class": "E1",
            "source_url": CS02_SOURCE_URL,
            "license": "CC BY 4.0 (UCI repository terms)",
            "retrieval_date_utc": now_utc,
            "raw_artifact": str(CS02_RAW.relative_to(ROOT)),
            "raw_sha256": _sha256(CS02_RAW),
            "transform_artifact": str(CS02_EXTRACT.relative_to(ROOT)),
            "transform_sha256": _sha256(CS02_EXTRACT),
            "rows": cs02_count,
            "notes": "Extracted continuous chemistry channels as taste-intensity proxy vectors.",
        },
        "CS-03": {
            "status": "READY",
            "name": "Chemosense multimodal fusion proxy pairs",
            "provenance_class": "real_public",
            "evidence_class": "E1",
            "source_url": "derived: CS-01 + CS-02 (public UCI datasets)",
            "license": "Derived from CC BY 4.0 upstream datasets",
            "retrieval_date_utc": now_utc,
            "raw_artifact": str(CS03_RAW.relative_to(ROOT)),
            "raw_sha256": _sha256(CS03_RAW),
            "transform_artifact": str(CS03_TRANSFORM.relative_to(ROOT)),
            "transform_sha256": _sha256(CS03_TRANSFORM),
            "rows": cs03_count,
            "notes": "Frame-aligned smell/taste rows with deterministic touch proxy for fusion scheduling validation.",
        },
    }

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Saved: {CS01_EXTRACT}")
    print(f"Saved: {CS02_EXTRACT}")
    print(f"Saved: {CS03_TRANSFORM}")
    print(f"Saved: {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
