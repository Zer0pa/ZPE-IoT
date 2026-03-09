#!/usr/bin/env python3
"""DT-24: Fusion packet-order determinism for taste->smell->touch streams."""

from __future__ import annotations

from _common import log_result, print_case
from zpe_iot.chemosense import encode_smell_payload, encode_touch_payload, taste


def _touch_packet(seed: int) -> list[int]:
    return encode_touch_payload(
        {
            "strokes": [
                {
                    "receptor": "SA_I",
                    "region": "INDEX_TIP",
                    "directions": [((seed * 2) + 1) % 8, ((seed * 2) + 2) % 8],
                    "pressure_profile": [2, 3],
                }
            ]
        }
    )


def _build_stream() -> tuple[list[int], list[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]], dict[str, int]]:
    taste_events = [
        taste.zlayered_event_from_vector((7, 1, 1, 0, 3), temporal_directions=(1, 1, 0, 0, 0, 7, 6, 6)),
        taste.zlayered_event_from_vector((1, 7, 2, 1, 1), temporal_directions=(0, 2, 4, 6, 0, 2, 4, 6)),
    ]

    smell_packets = [
        encode_smell_payload(
            {
                "strokes": [
                    {
                        "category": "FLORAL",
                        "pleasantness_start": 4,
                        "intensity_start": 1,
                        "directions": [0, 2, 4],
                    }
                ]
            }
        ),
        encode_smell_payload(
            {
                "strokes": [
                    {
                        "category": "WOODY_EARTHY",
                        "pleasantness_start": 3,
                        "intensity_start": 2,
                        "directions": [1, 3, 5],
                    }
                ]
            }
        ),
    ]
    touch_packets = [_touch_packet(0), _touch_packet(1)]

    words = taste.pack_fused_multimodal(
        taste_events=taste_events,
        smell_packets=smell_packets,
        touch_packets=touch_packets,
        adaptive=True,
    )

    scheduler = taste.FusionScheduler()
    ingest = scheduler.ingest_stream(words)
    events = scheduler.fuse_zlayer_events()
    emitted = scheduler.emit_fused_words()
    if emitted != words:
        raise RuntimeError("scheduler emit_fused_words does not preserve stream ordering")

    signatures = [event.signature() for event in events]
    return words, signatures, ingest


def main() -> int:
    try:
        words_a, sig_a, ingest_a = _build_stream()
        words_b, sig_b, ingest_b = _build_stream()
    except Exception as exc:
        print_case("FAIL", str(exc))
        log_result("DT-24", "FAIL", {}, notes=str(exc))
        return 1

    if words_a != words_b:
        msg = "Fused word stream is non-deterministic across equivalent runs"
        print_case("FAIL", msg)
        log_result("DT-24", "FAIL", {}, notes=msg)
        return 1

    if sig_a != sig_b:
        msg = "Fusion signatures changed across deterministic runs"
        print_case("FAIL", msg)
        log_result("DT-24", "FAIL", {}, notes=msg)
        return 1

    expected = {"taste_packets": 2, "smell_packets": 2, "touch_packets": 2}
    for key, value in expected.items():
        if int(ingest_a.get(key, -1)) != value or int(ingest_b.get(key, -1)) != value:
            msg = f"{key} mismatch expected {value}, got {ingest_a.get(key)} and {ingest_b.get(key)}"
            print_case("FAIL", msg)
            log_result("DT-24", "FAIL", {}, notes=msg)
            return 1

    print_case("PASS", "Fusion stream order, packet counts, and signatures remain deterministic")
    log_result("DT-24", "PASS", {"fused_word_count": len(words_a), "event_count": len(sig_a)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
