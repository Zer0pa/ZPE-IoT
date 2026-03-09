from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from zpe_iot.chemosense import (
    ChemosensePacketError,
    ChemosenseSchemaError,
    decode_mental_payload,
    decode_smell_payload,
    decode_taste_payload,
    decode_touch_payload,
    encode_mental_payload,
    encode_smell_payload,
    encode_taste_payload,
    encode_touch_payload,
    run_smoke_flow,
)
from zpe_iot.cli import main


def test_smell_contract_roundtrip_schema() -> None:
    payload = {
        "metadata": {"sniff_hz": 3},
        "strokes": [
            {
                "category": "FLORAL",
                "pleasantness_start": 4,
                "intensity_start": 1,
                "directions": [0, 2, 4],
            }
        ],
    }

    words = encode_smell_payload(payload)
    decoded = decode_smell_payload(words)

    assert isinstance(words, list) and words
    assert decoded["metadata"] == {"sniff_hz": 3}
    assert len(decoded["strokes"]) == 1
    assert decoded["strokes"][0]["category"] == "FLORAL"
    assert decoded["strokes"][0]["directions"] == [0, 2, 4]


def test_taste_contract_roundtrip_schema() -> None:
    payload = {
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

    words = encode_taste_payload(payload)
    decoded = decode_taste_payload(words)

    assert isinstance(words, list) and words
    assert decoded["metadata"]["event_count"] == 1
    assert decoded["events"][0]["dominant_quality"] == "SWEET"
    assert decoded["events"][0]["secondary_quality"] in {"SOUR", "UMAMI", "SALT", "BITTER", "SWEET"}
    assert len(decoded["events"][0]["temporal_directions"]) == 8


def test_contract_schema_error_surfaces() -> None:
    with pytest.raises(ChemosenseSchemaError):
        encode_smell_payload({"metadata": {"sniff_hz": 2}})

    with pytest.raises(ChemosenseSchemaError):
        encode_taste_payload(
            {
                "events": [
                    {
                        "quality_vector": [7, 1],
                        "temporal_directions": [0, 2, 4, 6, 0, 2, 4, 6],
                    }
                ]
            }
        )

    with pytest.raises(ChemosenseSchemaError):
        encode_touch_payload({"strokes": [{"receptor": "SA_I"}]})

    with pytest.raises(ChemosenseSchemaError):
        encode_mental_payload({"strokes": [{"form_class": "SPIRAL"}]})


def test_contract_packet_error_surfaces() -> None:
    with pytest.raises(ChemosensePacketError):
        decode_smell_payload([0x0001, 0x0002, 0x0003])

    with pytest.raises(ChemosensePacketError):
        decode_taste_payload([0x0001, 0x0002, 0x0003])

    with pytest.raises(ChemosensePacketError):
        decode_touch_payload([0x0001, 0x0002, 0x0003])

    with pytest.raises(ChemosensePacketError):
        decode_mental_payload([0x0001, 0x0002, 0x0003])


def test_touch_and_mental_contract_roundtrip_schema() -> None:
    touch_payload = {
        "strokes": [
            {
                "receptor": "SA_I",
                "region": "INDEX_TIP",
                "directions": [0, 2, 4],
                "pressure_profile": [2, 3, 2],
            }
        ]
    }
    mental_payload = {
        "strokes": [
            {
                "form_class": "SPIRAL",
                "symmetry": "D4",
                "direction_profile": "COMPASS_8",
                "spatial_frequency": 4,
                "drift_speed": 1,
                "frame_index": 2,
                "delta_ms": 17,
                "start": [128, 128],
                "directions": [0, 1, 2, 3],
            }
        ]
    }

    touch_words = encode_touch_payload(touch_payload)
    mental_words = encode_mental_payload(mental_payload)

    touch_decoded = decode_touch_payload(touch_words)
    mental_decoded = decode_mental_payload(mental_words)

    assert len(touch_decoded["strokes"]) == 1
    assert touch_decoded["strokes"][0]["region"] == "INDEX_TIP"
    assert touch_decoded["strokes"][0]["directions"] == [0, 2, 4]
    assert len(mental_decoded["strokes"]) == 1
    assert mental_decoded["strokes"][0]["direction_profile"] == "COMPASS_8"
    assert mental_decoded["strokes"][0]["directions"] == [0, 1, 2, 3]


def test_cli_smoke_uses_contract_primitives() -> None:
    runner = CliRunner()
    cli_result = runner.invoke(main, ["chemosense-smoke", "--json"])
    assert cli_result.exit_code == 0, cli_result.output

    cli_payload = json.loads(cli_result.output)
    api_payload = run_smoke_flow()

    assert cli_payload["command"] == "chemosense-smoke"
    assert cli_payload["smell_word_count"] == api_payload["smell_word_count"]
    assert cli_payload["taste_word_count"] == api_payload["taste_word_count"]
    assert cli_payload["touch_word_count"] == api_payload["touch_word_count"]
    assert cli_payload["mental_word_count"] == api_payload["mental_word_count"]
    assert cli_payload["fused_event_count"] == api_payload["fused_event_count"]
    assert cli_payload["touch_placeholder_removed"] is True
