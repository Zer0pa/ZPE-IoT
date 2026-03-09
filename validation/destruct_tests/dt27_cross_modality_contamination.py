#!/usr/bin/env python3
"""DT-27: Cross-modality contamination matrix for mental/smell/taste/touch streams."""

from __future__ import annotations

from _common import log_result, print_case
from zpe_iot.chemosense import (
    ChemosensePacketError,
    decode_mental_payload,
    decode_smell_payload,
    decode_taste_payload,
    decode_touch_payload,
    encode_mental_payload,
    encode_smell_payload,
    encode_taste_payload,
    encode_touch_payload,
)


def _sample_streams() -> dict[str, list[int]]:
    mental_words = encode_mental_payload(
        {
            "strokes": [
                {
                    "form_class": "SPIRAL",
                    "symmetry": "D4",
                    "direction_profile": "COMPASS_8",
                    "spatial_frequency": 4,
                    "drift_speed": 1,
                    "frame_index": 1,
                    "delta_ms": 20,
                    "start": [128, 128],
                    "directions": [0, 1, 2, 3],
                }
            ]
        }
    )
    smell_words = encode_smell_payload(
        {
            "metadata": {"sniff_hz": 3},
            "strokes": [
                {
                    "category": "FLORAL",
                    "pleasantness_start": 4,
                    "intensity_start": 2,
                    "directions": [0, 2, 4],
                }
            ],
        }
    )
    taste_words = encode_taste_payload(
        {
            "adaptive": True,
            "events": [
                {
                    "quality_vector": [7, 1, 1, 0, 3],
                    "temporal_directions": [1, 1, 0, 0, 0, 7, 6, 6],
                    "intensity_end": 4,
                    "flavor_link": [1, 2],
                }
            ],
        }
    )
    touch_words = encode_touch_payload(
        {
            "strokes": [
                {
                    "receptor": "SA_I",
                    "region": "INDEX_TIP",
                    "directions": [0, 2, 4],
                    "pressure_profile": [2, 3, 2],
                }
            ]
        }
    )

    return {
        "mental": mental_words,
        "smell": smell_words,
        "taste": taste_words,
        "touch": touch_words,
    }


def _decoder_map():
    return {
        "mental": decode_mental_payload,
        "smell": decode_smell_payload,
        "taste": decode_taste_payload,
        "touch": decode_touch_payload,
    }


def main() -> int:
    streams = _sample_streams()
    decoders = _decoder_map()

    false_positives: list[str] = []

    for target, decoder in decoders.items():
        for source, words in streams.items():
            if target == source:
                continue
            try:
                decoder(words)
                false_positives.append(f"{target} decoder accepted pure {source} stream")
            except ChemosensePacketError:
                pass
            except Exception as exc:
                false_positives.append(f"{target} decoder raised unexpected exception on {source}: {exc}")

    mixed = [*streams["mental"], *streams["smell"], *streams["taste"], *streams["touch"]]

    try:
        mixed_mental = decode_mental_payload(mixed)
        mixed_smell = decode_smell_payload(mixed)
        mixed_taste = decode_taste_payload(mixed)
        mixed_touch = decode_touch_payload(mixed)
    except Exception as exc:
        print_case("FAIL", f"mixed-stream decode failed: {exc}")
        log_result("DT-27", "FAIL", {"false_positives": len(false_positives)}, notes=f"mixed decode error: {exc}")
        return 1

    counts = {
        "mental": len(mixed_mental.get("strokes", [])),
        "smell": len(mixed_smell.get("strokes", [])),
        "taste": len(mixed_taste.get("events", [])),
        "touch": len(mixed_touch.get("strokes", [])),
    }

    for modality, count in counts.items():
        if count != 1:
            false_positives.append(f"mixed stream decoded {count} {modality} packet(s), expected 1")

    if false_positives:
        for issue in false_positives:
            print_case("FAIL", issue)
        log_result(
            "DT-27",
            "FAIL",
            {"false_positives": len(false_positives), **{f"mixed_{k}": v for k, v in counts.items()}},
            notes="; ".join(false_positives),
        )
        return 1

    print_case("PASS", "Mixed mental/smell/taste/touch streams showed zero false-positive decodes")
    log_result(
        "DT-27",
        "PASS",
        {"false_positives": 0, **{f"mixed_{k}": v for k, v in counts.items()}},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
