#!/usr/bin/env python3
"""DT-23: Z-layer decode integrity for chemosense taste events."""

from __future__ import annotations

from _common import log_result, print_case
from zpe_iot.chemosense import decode_taste_payload, encode_taste_payload


PAYLOAD = {
    "adaptive": True,
    "events": [
        {
            "quality_vector": [7, 1, 1, 0, 3],
            "temporal_directions": [1, 1, 0, 0, 0, 7, 6, 6],
            "intensity_end": 4,
            "flavor_link": [1, 2],
        },
        {
            "quality_vector": [1, 7, 2, 1, 1],
            "temporal_directions": [0, 2, 4, 6, 0, 2, 4, 6],
            "intensity_end": 2,
            "flavor_link": [2, 3],
        },
    ],
}


EXPECTED_DOMINANT = ["SWEET", "SOUR"]


def main() -> int:
    words = encode_taste_payload(PAYLOAD)
    decoded = decode_taste_payload(words)

    issues: list[str] = []

    metadata = decoded.get("metadata", {})
    if int(metadata.get("event_count", -1)) != 2:
        issues.append(f"metadata.event_count expected 2 got {metadata.get('event_count')}")

    events = decoded.get("events", [])
    if len(events) != 2:
        issues.append(f"decoded event count expected 2 got {len(events)}")
    else:
        dominant = [str(event.get("dominant_quality")) for event in events]
        if dominant != EXPECTED_DOMINANT:
            issues.append(f"dominant quality mismatch expected {EXPECTED_DOMINANT} got {dominant}")

        for idx, event in enumerate(events):
            temporal = event.get("temporal_directions", [])
            if len(temporal) != 8:
                issues.append(f"events[{idx}] temporal_directions length != 8")

            flavor = event.get("flavor_link")
            if flavor is None or len(flavor) != 2:
                issues.append(f"events[{idx}] flavor_link not preserved")

    if issues:
        for issue in issues:
            print_case("FAIL", issue)
        log_result("DT-23", "FAIL", {"issues": len(issues)}, notes="; ".join(issues))
        return 1

    print_case("PASS", "Z-layer encode/decode preserves event count, dominant quality, temporal vectors, and flavor links")
    log_result("DT-23", "PASS", {"word_count": len(words), "event_count": len(events)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
