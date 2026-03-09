#!/usr/bin/env python3
"""Run chemosense modality benchmarks with pinned baseline metadata."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import time
import zlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from zpe_iot.chemosense import (
    decode_mental_payload,
    decode_smell_payload,
    decode_taste_payload,
    decode_touch_payload,
    encode_mental_payload,
    encode_smell_payload,
    encode_taste_payload,
    encode_touch_payload,
    taste,
)

RESULTS_DIR = ROOT / "validation" / "results"
CHEMO_MANIFEST = ROOT / "validation" / "datasets" / "manifest_chemosense.json"
BASELINE_TAG_PATH = ROOT / "validation" / "results" / "baseline" / "ACTIVE_BASELINE_TAG"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _p(values: list[float], percentile: float) -> float:
    return float(np.percentile(values, percentile)) if values else 0.0


def _measure(fn, repeats: int = 7, warmup: int = 2) -> list[float]:
    timings: list[float] = []
    for idx in range(max(1, repeats) + max(0, warmup)):
        t0 = time.perf_counter()
        fn()
        elapsed = (time.perf_counter() - t0) * 1000.0
        if idx >= warmup:
            timings.append(elapsed)
    return timings


def _load_manifest() -> dict:
    if not CHEMO_MANIFEST.exists():
        raise RuntimeError(f"Missing chemosense manifest: {CHEMO_MANIFEST}")
    return json.loads(CHEMO_MANIFEST.read_text(encoding="utf-8"))


def _load_csv_rows(path: Path, limit: int = 256) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            if len(rows) >= limit:
                break
    return rows


def _smell_payload(rows: list[dict[str, str]]) -> dict:
    categories = ["FLORAL", "FRUITY", "SPICY_HERBAL", "WOODY_EARTHY"]
    strokes = []
    for idx, row in enumerate(rows):
        co = float(row["co_gt"])
        s1 = float(row["pt08_s1_co"])
        s2 = float(row["pt08_s2_nmhc"])
        s3 = float(row["pt08_s3_nox"])
        directions = [int(abs(v) * 10.0) % 8 for v in (co, s1, s2, s3, co + s1, s2 + s3)]
        strokes.append(
            {
                "category": categories[idx % len(categories)],
                "pleasantness_start": int(abs(co)) % 8,
                "intensity_start": int(abs(s3)) % 8,
                "directions": directions,
            }
        )
    return {"metadata": {"sniff_hz": 4}, "strokes": strokes}


def _taste_payload(rows: list[dict[str, str]]) -> dict:
    events = []
    for idx, row in enumerate(rows):
        vals = [
            float(row["fixed_acidity"]),
            float(row["volatile_acidity"]),
            float(row["citric_acid"]),
            float(row["chlorides"]),
            float(row["residual_sugar"]),
            float(row["quality"]),
        ]
        quality_vector = [
            int(abs(vals[0]) * 2) % 8,
            int(abs(vals[1]) * 10) % 8,
            int(abs(vals[2]) * 20) % 8,
            int(abs(vals[3]) * 100) % 8,
            int(abs(vals[5])) % 8,
        ]
        temporal = [int(abs(vals[(j + idx) % len(vals)]) * 7) % 8 for j in range(8)]
        events.append(
            {
                "quality_vector": quality_vector,
                "temporal_directions": temporal,
                "intensity_end": int(abs(vals[4]) * 2) % 8,
                "flavor_link": [idx % 8, (idx + 1) % 8],
            }
        )
    return {"adaptive": True, "events": events}


def _touch_payload(rows: list[dict[str, str]]) -> dict:
    regions = ["INDEX_TIP", "MIDDLE_TIP", "PALM_CENTER", "THUMB_TIP", "WRIST_FOREARM"]
    strokes = []
    for idx, row in enumerate(rows):
        co = float(row["co_gt"])
        s1 = float(row["pt08_s1_co"])
        s2 = float(row["pt08_s2_nmhc"])
        s3 = float(row["pt08_s3_nox"])
        directions = [
            int(abs(co) * 10.0) % 8,
            int(abs(s1) * 10.0) % 8,
            int(abs(s2) * 10.0) % 8,
        ]
        pressures = [
            int(abs(s3) * 2.0) % 8,
            int(abs(co + s1) * 2.0) % 8,
            int(abs(s2 + s3) * 2.0) % 8,
        ]
        strokes.append(
            {
                "receptor": "RA_II" if (idx % 3 == 0) else "SA_I",
                "region": regions[idx % len(regions)],
                "directions": directions,
                "pressure_profile": pressures,
            }
        )
    return {"strokes": strokes}


def _mental_payload(rows: list[dict[str, str]]) -> dict:
    strokes = []
    for idx, row in enumerate(rows):
        vals = [
            float(row["fixed_acidity"]),
            float(row["volatile_acidity"]),
            float(row["citric_acid"]),
            float(row["chlorides"]),
            float(row["residual_sugar"]),
            float(row["quality"]),
        ]
        is_d12 = (idx % 3) == 0
        if is_d12:
            directions = [int(abs(vals[(j + idx) % len(vals)]) * 12.0) % 12 for j in range(6)]
            direction_profile = "D6_12"
            symmetry = "D6"
        else:
            directions = [int(abs(vals[(j + idx) % len(vals)]) * 8.0) % 8 for j in range(8)]
            direction_profile = "COMPASS_8"
            symmetry = "D4"
        strokes.append(
            {
                "form_class": ["TUNNEL", "SPIRAL", "LATTICE", "COBWEB"][idx % 4],
                "symmetry": symmetry,
                "direction_profile": direction_profile,
                "spatial_frequency": int(abs(vals[0]) * 2.0) % 8,
                "drift_speed": int(abs(vals[1]) * 2.0) % 4,
                "frame_index": idx % 255,
                "delta_ms": int(abs(vals[2]) * 100.0) % 255,
                "start": [int(abs(vals[3]) * 100.0) % 255, int(abs(vals[4]) * 100.0) % 255],
                "directions": directions,
            }
        )
    return {"metadata": {"use_rle": True}, "strokes": strokes}


def _modality_metrics(payload: dict, encode_fn, decode_fn) -> dict:
    encoded = encode_fn(payload)
    raw_bytes = len(json.dumps(payload, sort_keys=True).encode("utf-8"))
    packed_bytes = len(encoded) * 4

    enc_ms = _measure(lambda: encode_fn(payload), repeats=7, warmup=2)
    dec_ms = _measure(lambda: decode_fn(encoded), repeats=7, warmup=2)

    baseline = zlib.compress(json.dumps(payload, sort_keys=True).encode("utf-8"), level=6)
    zlib_cr = raw_bytes / max(1, len(baseline))
    zpe_cr = raw_bytes / max(1, packed_bytes)

    return {
        "raw_bytes": raw_bytes,
        "packed_bytes": packed_bytes,
        "zpe_cr": float(zpe_cr),
        "zlib_cr": float(zlib_cr),
        "winner": "zpe-iot" if zpe_cr >= zlib_cr else "zlib",
        "encode_ms_p50": _p(enc_ms, 50),
        "encode_ms_p99": _p(enc_ms, 99),
        "decode_ms_p50": _p(dec_ms, 50),
        "decode_ms_p99": _p(dec_ms, 99),
    }


def _fusion_metrics(smell_payload: dict, taste_payload: dict, touch_payload: dict) -> dict:
    smell_packets = [encode_smell_payload({"strokes": [stroke]}) for stroke in smell_payload["strokes"][:128]]
    taste_events = [
        taste.zlayered_event_from_vector(
            quality_vector=tuple(event["quality_vector"]),
            temporal_directions=tuple(event["temporal_directions"]),
            intensity_end=int(event["intensity_end"]),
            flavor_link=(int(event["flavor_link"][0]), int(event["flavor_link"][1])),
        )
        for event in taste_payload["events"][:128]
    ]
    touch_packets = [
        encode_touch_payload({"strokes": [stroke]})
        for stroke in touch_payload["strokes"][: len(taste_events)]
    ]

    words = taste.pack_fused_multimodal(
        taste_events=taste_events,
        smell_packets=smell_packets,
        touch_packets=touch_packets,
        adaptive=True,
    )

    def _run_scheduler() -> dict:
        scheduler = taste.FusionScheduler()
        ingest = scheduler.ingest_stream(words)
        fused = scheduler.fuse_zlayer_events()
        return {
            "taste_packets": int(ingest["taste_packets"]),
            "smell_packets": int(ingest["smell_packets"]),
            "touch_packets": int(ingest["touch_packets"]),
            "fused_events": int(len(fused)),
        }

    ingest_ms = _measure(_run_scheduler, repeats=7, warmup=2)
    result = _run_scheduler()

    raw_json = json.dumps(
        {
            "taste_events": taste_payload["events"][: len(taste_events)],
            "smell_strokes": smell_payload["strokes"][: len(smell_packets)],
            "touch_strokes": touch_payload["strokes"][: len(touch_packets)],
        },
        sort_keys=True,
    ).encode("utf-8")
    zlib_bytes = zlib.compress(raw_json, level=6)

    return {
        "raw_bytes": len(raw_json),
        "packed_bytes": len(words) * 4,
        "zpe_cr": float(len(raw_json) / max(1, len(words) * 4)),
        "zlib_cr": float(len(raw_json) / max(1, len(zlib_bytes))),
        "winner": "zpe-iot" if (len(raw_json) / max(1, len(words) * 4)) >= (len(raw_json) / max(1, len(zlib_bytes))) else "zlib",
        "ingest_ms_p50": _p(ingest_ms, 50),
        "ingest_ms_p99": _p(ingest_ms, 99),
        "counts": result,
        "fused_word_count": len(words),
    }


def main() -> int:
    manifest = _load_manifest()

    cs01 = ROOT / manifest["CS-01"]["transform_artifact"]
    cs02 = ROOT / manifest["CS-02"]["transform_artifact"]

    smell_rows = _load_csv_rows(cs01, limit=256)
    taste_rows = _load_csv_rows(cs02, limit=256)

    smell_payload = _smell_payload(smell_rows)
    taste_payload = _taste_payload(taste_rows)
    touch_payload = _touch_payload(smell_rows)
    mental_payload = _mental_payload(taste_rows)

    smell_metrics = _modality_metrics(smell_payload, encode_smell_payload, decode_smell_payload)
    taste_metrics = _modality_metrics(taste_payload, encode_taste_payload, decode_taste_payload)
    touch_metrics = _modality_metrics(touch_payload, encode_touch_payload, decode_touch_payload)
    mental_metrics = _modality_metrics(mental_payload, encode_mental_payload, decode_mental_payload)
    fusion_metrics = _fusion_metrics(smell_payload, taste_payload, touch_payload)

    rows = [
        {
            "dataset": "CS-01",
            "modality": "smell",
            "evidence_class": manifest["CS-01"].get("evidence_class", "E0"),
            **smell_metrics,
        },
        {
            "dataset": "CS-02",
            "modality": "taste",
            "evidence_class": manifest["CS-02"].get("evidence_class", "E0"),
            **taste_metrics,
        },
        {
            "dataset": "CS-03",
            "modality": "fusion",
            "evidence_class": manifest["CS-03"].get("evidence_class", "E0"),
            **fusion_metrics,
        },
        {
            "dataset": "CS-04",
            "modality": "touch",
            "evidence_class": manifest.get("CS-04", {}).get("evidence_class", "E0"),
            **touch_metrics,
        },
        {
            "dataset": "CS-05",
            "modality": "mental",
            "evidence_class": manifest.get("CS-05", {}).get("evidence_class", "E0"),
            **mental_metrics,
        },
    ]

    wins = sum(1 for row in rows if row.get("winner") == "zpe-iot")
    total = len(rows)

    baseline_tag = os.getenv("ZPE_IOT_BASELINE_TAG", "").strip()
    if not baseline_tag and BASELINE_TAG_PATH.exists():
        baseline_tag = BASELINE_TAG_PATH.read_text(encoding="utf-8").strip()

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    payload = {
        "timestamp": timestamp,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "baseline_tag": baseline_tag or None,
        "evidence_class": "E1",
        "datasets": rows,
        "wins": wins,
        "total": total,
        "chemosense_gate_pass": bool(wins >= 3),
        "method_metadata": {
            "pathway": "encode_words_then_decode_words",
            "repeats": 7,
            "warmup": 2,
            "comparators": ["zlib(level=6)"],
            "fairness": "same payload object encoded by zpe chemosense and zlib JSON envelope across smell/taste/touch/mental/fusion",
            "modalities_benchmarked": ["smell", "taste", "touch", "mental", "fusion"],
        },
        "reproducibility": {
            "manifest_path": str(CHEMO_MANIFEST),
            "manifest_sha256": _sha256(CHEMO_MANIFEST),
            "command": "python validation/benchmarks/run_chemosense_benchmarks.py",
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"bench_summary_chemosense_{timestamp}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"Saved: {out}")
    print(f"Chemosense benchmark wins: {wins}/{total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
