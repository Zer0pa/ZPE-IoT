#!/usr/bin/env python3
"""Profile chemosense hot paths and emit performance/tightness artifacts."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from zpe_iot.chemosense import decode_smell_payload, decode_taste_payload, encode_smell_payload, encode_taste_payload
from zpe_iot.chemosense import taste

RESULTS_DIR = ROOT / "validation" / "results"
PERF_DOC_DIR = ROOT / "docs" / "perf"


def _p(values: list[float], percentile: float) -> float:
    return float(np.percentile(values, percentile)) if values else 0.0


def _measure(fn, repeats: int = 7, warmup: int = 2) -> list[float]:
    timings: list[float] = []
    total = max(1, repeats) + max(0, warmup)
    for i in range(total):
        t0 = time.perf_counter()
        fn()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if i >= warmup:
            timings.append(elapsed_ms)
    return timings


def _smell_payload(count: int = 64) -> dict:
    categories = [
        "FLORAL",
        "WOODY_EARTHY",
        "FRUITY",
        "SPICY_HERBAL",
    ]
    strokes = []
    for idx in range(count):
        strokes.append(
            {
                "category": categories[idx % len(categories)],
                "pleasantness_start": (idx + 3) % 8,
                "intensity_start": (idx + 1) % 8,
                "directions": [(idx + k) % 8 for k in range(6)],
            }
        )
    return {"metadata": {"sniff_hz": 4}, "strokes": strokes}


def _taste_payload(count: int = 64) -> dict:
    events = []
    for idx in range(count):
        events.append(
            {
                "quality_vector": [
                    7 if idx % 2 == 0 else 1,
                    1 if idx % 3 == 0 else 7,
                    (idx + 1) % 8,
                    idx % 4,
                    (3 + idx) % 8,
                ],
                "temporal_directions": [(idx + j) % 8 for j in range(8)],
                "intensity_end": (2 + idx) % 8,
                "flavor_link": [idx % 8, (idx + 1) % 8],
            }
        )
    return {"adaptive": True, "events": events}


def _legacy_extract_taste_packets(words: list[int]) -> list[list[int]]:
    packets: list[list[int]] = []
    index = 0

    while index < len(words):
        first = taste.unpack_taste_zlevel_word(words[index])
        if first is None or first[0] != taste.TasteZLevel.QUALITY:
            index += 1
            continue
        if index + 3 >= len(words):
            break

        second = taste.unpack_taste_zlevel_word(words[index + 1])
        t0 = taste.unpack_taste_zlevel_word(words[index + 2])
        t1 = taste.unpack_taste_zlevel_word(words[index + 3])
        if (
            second is None
            or second[0] != taste.TasteZLevel.INTENSITY
            or t0 is None
            or t0[0] != taste.TasteZLevel.TEMPORAL
            or t1 is None
            or t1[0] != taste.TasteZLevel.TEMPORAL
        ):
            index += 1
            continue

        use_coarse = (second[1] & 0x80) != 0
        consumed = 4
        if not use_coarse:
            if index + 4 >= len(words):
                break
            t2 = taste.unpack_taste_zlevel_word(words[index + 4])
            if t2 is None or t2[0] != taste.TasteZLevel.TEMPORAL:
                index += 1
                continue
            consumed = 5

        maybe_flavor_index = index + consumed
        if maybe_flavor_index < len(words):
            maybe_flavor = taste.unpack_taste_zlevel_word(words[maybe_flavor_index])
            if maybe_flavor is not None and maybe_flavor[0] == taste.TasteZLevel.FLAVOR:
                consumed += 1

        packets.append(words[index : index + consumed])
        index += consumed

    return packets


def _legacy_extract_smell_packets(words: list[int]) -> list[list[int]]:
    packets: list[list[int]] = []
    index = 0

    while index < len(words):
        word = words[index]
        mode = (word >> 18) & 0x3
        version = (word >> 16) & 0x3
        payload = word & 0xFFFF
        is_smell = mode == 0b10 and (word & 0x0200) != 0
        if not is_smell or version != 0:
            index += 1
            continue

        op = (payload >> 6) & 0x3
        if op != 0:
            index += 1
            continue
        if index + 1 >= len(words):
            break

        second_word = words[index + 1]
        mode_b = (second_word >> 18) & 0x3
        version_b = (second_word >> 16) & 0x3
        payload_b = second_word & 0xFFFF
        is_smell_b = mode_b == 0b10 and (second_word & 0x0200) != 0
        if not is_smell_b or version_b != 0:
            index += 1
            continue
        op_b = (payload_b >> 6) & 0x3
        if op_b != 1:
            index += 1
            continue

        step_count = payload_b & 0x7
        consumed = 2
        cursor = index + 2
        while consumed < 2 + step_count and cursor < len(words):
            step_word = words[cursor]
            mode_s = (step_word >> 18) & 0x3
            version_s = (step_word >> 16) & 0x3
            payload_s = step_word & 0xFFFF
            is_smell_s = mode_s == 0b10 and (step_word & 0x0200) != 0
            if not is_smell_s or version_s != 0 or ((payload_s >> 6) & 0x3) != 2:
                break
            consumed += 1
            cursor += 1

        while cursor < len(words):
            meta_word = words[cursor]
            mode_m = (meta_word >> 18) & 0x3
            version_m = (meta_word >> 16) & 0x3
            payload_m = meta_word & 0xFFFF
            is_smell_m = mode_m == 0b10 and (meta_word & 0x0200) != 0
            if not is_smell_m or version_m != 0 or ((payload_m >> 6) & 0x3) != 3:
                break
            consumed += 1
            cursor += 1

        packets.append(words[index : index + consumed])
        index += consumed

    return packets


def _legacy_extract_touch_packets(words: list[int]) -> list[list[int]]:
    packets: list[list[int]] = []
    index = 0

    while index < len(words):
        header = words[index]
        mode = (header >> 18) & 0x3
        version = (header >> 16) & 0x3
        is_touch = mode == 0b10 and (header & 0x0800) != 0
        is_touch_header = is_touch and version == 1 and (header & 0x001F) == 0x001F
        if not is_touch_header:
            index += 1
            continue

        cursor = index + 1
        while cursor < len(words):
            word = words[cursor]
            mode = (word >> 18) & 0x3
            version = (word >> 16) & 0x3
            is_touch = mode == 0b10 and (word & 0x0800) != 0
            if not is_touch:
                break
            if version == 1 and (word & 0x001F) == 0x001F:
                break
            if version != 0:
                break
            cursor += 1

        packets.append(words[index:cursor])
        index = cursor

    return packets


def _legacy_fusion_ingest(words: list[int]) -> dict[str, int]:
    taste_packets = _legacy_extract_taste_packets(words)
    smell_packets = _legacy_extract_smell_packets(words)
    touch_packets = _legacy_extract_touch_packets(words)

    boundary = min(len(taste_packets), len(smell_packets), len(touch_packets))
    fused_events = 0
    for idx in range(boundary):
        _meta, decoded = taste.unpack_taste_zlayered(taste_packets[idx])
        if decoded:
            fused_events += 1

    return {
        "taste_packets": len(taste_packets),
        "smell_packets": len(smell_packets),
        "touch_packets": len(touch_packets),
        "fused_events": fused_events,
    }


def _scheduler_fusion_ingest(words: list[int]) -> dict[str, int]:
    scheduler = taste.FusionScheduler()
    ingest = scheduler.ingest_stream(words)
    fused = scheduler.fuse_zlayer_events()
    return {
        "taste_packets": int(ingest["taste_packets"]),
        "smell_packets": int(ingest["smell_packets"]),
        "touch_packets": int(ingest["touch_packets"]),
        "fused_events": int(len(fused)),
    }


def main() -> int:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PERF_DOC_DIR.mkdir(parents=True, exist_ok=True)

    smell_payload = _smell_payload(count=64)
    taste_payload = _taste_payload(count=64)

    encoded_smell = encode_smell_payload(smell_payload)
    encoded_taste = encode_taste_payload(taste_payload)

    taste_events = [
        taste.zlayered_event_from_vector(
            quality_vector=tuple(event["quality_vector"]),
            temporal_directions=tuple(event["temporal_directions"]),
            intensity_end=int(event["intensity_end"]),
            flavor_link=(int(event["flavor_link"][0]), int(event["flavor_link"][1])),
        )
        for event in taste_payload["events"]
    ]
    smell_packets = [encode_smell_payload({"strokes": [stroke]}) for stroke in smell_payload["strokes"]]
    touch_packets = []
    for idx in range(len(taste_events)):
        touch_type = 0x0800
        header_tag = 0x001F
        header = (0b10 << 18) | ((1 & 0x3) << 16) | (touch_type | header_tag | ((idx & 0x7) << 5))
        data0 = (0b10 << 18) | ((0 & 0x3) << 16) | (touch_type | ((idx * 2 + 1) & 0xFF))
        data1 = (0b10 << 18) | ((0 & 0x3) << 16) | (touch_type | ((idx * 2 + 2) & 0xFF))
        touch_packets.append([header, data0, data1])

    fused_words = taste.pack_fused_multimodal(
        taste_events=taste_events,
        smell_packets=smell_packets,
        touch_packets=touch_packets,
        adaptive=True,
    )

    smell_encode_ms = _measure(lambda: encode_smell_payload(smell_payload))
    smell_decode_ms = _measure(lambda: decode_smell_payload(encoded_smell))
    taste_encode_ms = _measure(lambda: encode_taste_payload(taste_payload))
    taste_decode_ms = _measure(lambda: decode_taste_payload(encoded_taste))

    fusion_legacy_ms = _measure(lambda: _legacy_fusion_ingest(fused_words), repeats=9, warmup=2)
    fusion_current_ms = _measure(lambda: _scheduler_fusion_ingest(fused_words), repeats=9, warmup=2)

    legacy_counts = _legacy_fusion_ingest(fused_words)
    current_counts = _scheduler_fusion_ingest(fused_words)

    legacy_p50 = _p(fusion_legacy_ms, 50)
    current_p50 = _p(fusion_current_ms, 50)
    median_improvement = ((legacy_p50 - current_p50) / legacy_p50) if legacy_p50 > 0 else 0.0

    payload = {
        "timestamp": timestamp,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "method": {
            "repeats": 9,
            "warmup": 2,
            "smell_stroke_count": len(smell_payload["strokes"]),
            "taste_event_count": len(taste_payload["events"]),
            "fused_word_count": len(fused_words),
            "pathway": "encode_words_then_decode_words",
        },
        "smell": {
            "encode_ms_mean": mean(smell_encode_ms),
            "encode_ms_p50": _p(smell_encode_ms, 50),
            "encode_ms_p99": _p(smell_encode_ms, 99),
            "decode_ms_mean": mean(smell_decode_ms),
            "decode_ms_p50": _p(smell_decode_ms, 50),
            "decode_ms_p99": _p(smell_decode_ms, 99),
        },
        "taste": {
            "encode_ms_mean": mean(taste_encode_ms),
            "encode_ms_p50": _p(taste_encode_ms, 50),
            "encode_ms_p99": _p(taste_encode_ms, 99),
            "decode_ms_mean": mean(taste_decode_ms),
            "decode_ms_p50": _p(taste_decode_ms, 50),
            "decode_ms_p99": _p(taste_decode_ms, 99),
        },
        "fusion": {
            "legacy_ingest_ms_mean": mean(fusion_legacy_ms),
            "legacy_ingest_ms_p50": legacy_p50,
            "legacy_ingest_ms_p99": _p(fusion_legacy_ms, 99),
            "current_ingest_ms_mean": mean(fusion_current_ms),
            "current_ingest_ms_p50": current_p50,
            "current_ingest_ms_p99": _p(fusion_current_ms, 99),
            "median_improvement_ratio": median_improvement,
            "median_improvement_pct": median_improvement * 100.0,
            "improved": current_p50 < legacy_p50,
            "legacy_counts": legacy_counts,
            "current_counts": current_counts,
        },
    }

    json_path = RESULTS_DIR / f"perf_profile_chemosense_{timestamp}.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md_path = PERF_DOC_DIR / f"chemosense_profile_{timestamp}.md"
    md_path.write_text(
        "\n".join(
            [
                "# Chemosense Performance Profile",
                "",
                f"- Timestamp: `{timestamp}`",
                "- Pathway: `encode_words_then_decode_words`",
                f"- Smell encode p50/p99: `{payload['smell']['encode_ms_p50']:.3f} / {payload['smell']['encode_ms_p99']:.3f} ms`",
                f"- Smell decode p50/p99: `{payload['smell']['decode_ms_p50']:.3f} / {payload['smell']['decode_ms_p99']:.3f} ms`",
                f"- Taste encode p50/p99: `{payload['taste']['encode_ms_p50']:.3f} / {payload['taste']['encode_ms_p99']:.3f} ms`",
                f"- Taste decode p50/p99: `{payload['taste']['decode_ms_p50']:.3f} / {payload['taste']['decode_ms_p99']:.3f} ms`",
                "",
                "## Fusion Ingest Tightness",
                f"- Legacy ingest p50/p99: `{payload['fusion']['legacy_ingest_ms_p50']:.3f} / {payload['fusion']['legacy_ingest_ms_p99']:.3f} ms`",
                f"- Current ingest p50/p99: `{payload['fusion']['current_ingest_ms_p50']:.3f} / {payload['fusion']['current_ingest_ms_p99']:.3f} ms`",
                f"- Median latency improvement: `{payload['fusion']['median_improvement_pct']:.2f}%`",
                f"- Improvement gate (current < legacy): `{payload['fusion']['improved']}`",
                "",
                "## Invariant Check",
                f"- Legacy packet counts: `{payload['fusion']['legacy_counts']}`",
                f"- Current packet counts: `{payload['fusion']['current_counts']}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Saved: {json_path}")
    print(f"Saved: {md_path}")
    print(
        "Fusion median improvement "
        f"{payload['fusion']['median_improvement_pct']:.2f}% "
        f"(legacy={legacy_p50:.3f}ms current={current_p50:.3f}ms)"
    )

    return 0 if payload["fusion"]["improved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
