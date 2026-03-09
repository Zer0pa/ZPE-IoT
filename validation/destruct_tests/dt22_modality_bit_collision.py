#!/usr/bin/env python3
"""DT-22: Chemosense modality bit-collision invariants."""

from __future__ import annotations

from _common import log_result, print_case
from zpe_iot.chemosense import (
    encode_mental_payload,
    encode_smell_payload,
    encode_taste_payload,
    encode_touch_payload,
)

MENTAL_TYPE_BIT = 0x0100
SMELL_TYPE_BIT = 0x0200
TASTE_TYPE_BIT = 0x0400
TOUCH_TYPE_BIT = 0x0800



def _is_extension(word: int) -> bool:
    return ((int(word) >> 18) & 0x3) == 0b10


def _is_mental_wire_mode(word: int) -> bool:
    return ((int(word) >> 18) & 0x3) in {0b10, 0b11}


def main() -> int:
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
                    "start": [64, 64],
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
                    "directions": [0, 2, 4, 6],
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

    issues: list[str] = []

    for idx, word in enumerate(mental_words):
        if not _is_mental_wire_mode(word):
            issues.append(f"mental[{idx}] is not mode2/mode3 wire-mode")
            continue
        payload = int(word) & 0xFFFF
        if (payload & MENTAL_TYPE_BIT) == 0:
            issues.append(f"mental[{idx}] missing mental type bit")
        # Mental control words run in mode=3 and may use high payload bits for
        # internal form/symmetry tags; enforce collision safety only on mode=2
        # data words that share the extension dispatch lane.
        if ((int(word) >> 18) & 0x3) == 0b10:
            if (payload & SMELL_TYPE_BIT) != 0:
                issues.append(f"mental[{idx}] collides with smell type bit")
            if (payload & TASTE_TYPE_BIT) != 0:
                issues.append(f"mental[{idx}] collides with taste type bit")
            if (payload & TOUCH_TYPE_BIT) != 0:
                issues.append(f"mental[{idx}] collides with touch type bit")

    for idx, word in enumerate(smell_words):
        if not _is_extension(word):
            issues.append(f"smell[{idx}] is not extension-mode")
            continue
        payload = int(word) & 0xFFFF
        if (payload & SMELL_TYPE_BIT) == 0:
            issues.append(f"smell[{idx}] missing smell type bit")
        if (payload & TASTE_TYPE_BIT) != 0:
            issues.append(f"smell[{idx}] collides with taste type bit")
        if (payload & TOUCH_TYPE_BIT) != 0:
            issues.append(f"smell[{idx}] collides with touch type bit")

    for idx, word in enumerate(taste_words):
        if not _is_extension(word):
            issues.append(f"taste[{idx}] is not extension-mode")
            continue
        payload = int(word) & 0xFFFF
        if (payload & TASTE_TYPE_BIT) == 0:
            issues.append(f"taste[{idx}] missing taste type bit")
        if (payload & SMELL_TYPE_BIT) != 0:
            issues.append(f"taste[{idx}] collides with smell type bit")
        if (payload & TOUCH_TYPE_BIT) != 0:
            issues.append(f"taste[{idx}] collides with touch type bit")
        if (payload & MENTAL_TYPE_BIT) != 0:
            issues.append(f"taste[{idx}] collides with mental type bit")

    for idx, word in enumerate(touch_words):
        if not _is_extension(word):
            issues.append(f"touch[{idx}] is not extension-mode")
            continue
        payload = int(word) & 0xFFFF
        if (payload & TOUCH_TYPE_BIT) == 0:
            issues.append(f"touch[{idx}] missing touch type bit")
        if (payload & SMELL_TYPE_BIT) != 0:
            issues.append(f"touch[{idx}] collides with smell type bit")
        if (payload & TASTE_TYPE_BIT) != 0:
            issues.append(f"touch[{idx}] collides with taste type bit")
        if (payload & MENTAL_TYPE_BIT) != 0:
            issues.append(f"touch[{idx}] collides with mental type bit")

    if issues:
        for issue in issues:
            print_case("FAIL", issue)
        log_result("DT-22", "FAIL", {"issues": len(issues)}, notes="; ".join(issues))
        return 1

    print_case("PASS", "Mental/smell/taste/touch extension words are collision-free across modality type bits")
    log_result(
        "DT-22",
        "PASS",
        {
            "mental_words": len(mental_words),
            "smell_words": len(smell_words),
            "taste_words": len(taste_words),
            "touch_words": len(touch_words),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
