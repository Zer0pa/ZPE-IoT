from __future__ import annotations

import json
from pathlib import Path

from zpe_iot.chemosense import touch
from zpe_iot.chemosense.touch import anatomy, phase5_extensions as p5
from zpe_iot.chemosense.touch import receptor_model as rmodel

TOUCH_BIT = 0x0800
COLLISION_BITS = 0x8000 | 0x4000 | 0x2000 | 0x1000

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "real_haptic_patterns.json"


def _make_stroke(
    receptor: touch.ReceptorType,
    region: touch.BodyRegion,
    directions: list[int],
    pressures: list[int],
) -> touch.TouchStroke:
    commands = [touch.MoveTo(0, 0)] + [touch.DrawDir(direction) for direction in directions]
    return touch.TouchStroke(
        commands=commands,
        receptor=receptor,
        region=region,
        pressure_profile=pressures,
    )


def _dirs(stroke: touch.TouchStroke) -> list[int]:
    return [cmd.direction for cmd in stroke.commands if isinstance(cmd, touch.DrawDir)]


def test_touch_pack_unpack_and_modality_bits() -> None:
    strokes = [
        _make_stroke(
            receptor=touch.ReceptorType.SA_I,
            region=touch.BodyRegion.INDEX_TIP,
            directions=[0, 0, 6, 6],
            pressures=[2, 3, 4, 5],
        ),
        _make_stroke(
            receptor=touch.ReceptorType.RA_I,
            region=touch.BodyRegion.PALM_CENTER,
            directions=[4, 4, 2],
            pressures=[1, 1, 2],
        ),
    ]

    words = touch.pack_touch_strokes(strokes)
    assert len(words) > 0
    assert all((word & TOUCH_BIT) != 0 for word in words)
    assert all((word & COLLISION_BITS) == 0 for word in words)

    metadata, decoded = touch.unpack_touch_words(words)
    assert metadata is not None
    assert metadata["header_words"] == 2
    assert len(decoded) == 2

    assert decoded[0].receptor == touch.ReceptorType.SA_I
    assert decoded[0].region == touch.BodyRegion.INDEX_TIP
    assert _dirs(decoded[0]) == [0, 0, 6, 6]
    assert decoded[0].pressure_profile == [2, 3, 4, 5]

    assert decoded[1].receptor == touch.ReceptorType.RA_I
    assert decoded[1].region == touch.BodyRegion.PALM_CENTER
    assert _dirs(decoded[1]) == [4, 4, 2]
    assert decoded[1].pressure_profile == [1, 1, 2]


def test_touch_exhaustive_receptor_region_direction_roundtrip() -> None:
    attempts = 0
    matches = 0

    for receptor in touch.ReceptorType:
        for region in touch.BodyRegion:
            for direction in range(8):
                stroke = _make_stroke(
                    receptor=receptor,
                    region=region,
                    directions=[direction],
                    pressures=[direction % 8],
                )
                words = touch.pack_touch_strokes([stroke])
                _, decoded = touch.unpack_touch_words(words)
                attempts += 1
                if (
                    decoded
                    and decoded[0].receptor == receptor
                    and decoded[0].region == region
                    and _dirs(decoded[0]) == [direction]
                    and decoded[0].pressure_profile == [direction % 8]
                ):
                    matches += 1

    assert attempts == 8 * 4 * 16
    assert matches == attempts


def test_touch_zlayers_anatomy_and_cross_modal_dispatch() -> None:
    z_words = touch.pack_touch_zlayers(
        directions=[0, 1, 2, 3],
        pressures=[2, 4, 6],
        region=touch.BodyRegion.PALM_CENTER,
    )
    decoded = touch.unpack_touch_zlayers(z_words)
    assert decoded["surface"] == [0, 1, 2, 3]
    assert decoded["dermal"] == [2, 4, 6]
    assert decoded["anatomical_region"] == touch.BodyRegion.PALM_CENTER

    for region in touch.BodyRegion:
        coord = anatomy.region_to_coordinate(region)
        assert anatomy.coordinate_to_region(coord) == region

    stroke = _make_stroke(
        receptor=touch.ReceptorType.SA_I,
        region=touch.BodyRegion.PALM_CENTER,
        directions=[0, 6, 4],
        pressures=[2, 3, 2],
    )
    touch_words = touch.pack_touch_strokes([stroke])

    text_word = (0b10 << 18) | (0 << 16) | 0x1000 | 0x0005
    mixed_stream = [touch_words[0], z_words[0], text_word, *touch_words[1:], *z_words[1:]]

    _, decoded_touch = touch.unpack_touch_words(mixed_stream)
    decoded_z = touch.unpack_touch_zlayers(mixed_stream)

    assert len(decoded_touch) == 1
    assert _dirs(decoded_touch[0]) == [0, 6, 4]
    assert decoded_z["surface"] == [0, 1, 2, 3]
    assert decoded_z["dermal"] == [2, 4, 6]
    assert decoded_z["anatomical_region"] == touch.BodyRegion.PALM_CENTER


def test_touch_temporal_frame_precision_and_ordering() -> None:
    contacts = [
        _make_stroke(touch.ReceptorType.SA_I, touch.BodyRegion.THUMB_TIP, [2, 6], [3, 2]),
        _make_stroke(touch.ReceptorType.SA_I, touch.BodyRegion.INDEX_TIP, [0, 4], [2, 2]),
        _make_stroke(touch.ReceptorType.SA_I, touch.BodyRegion.MIDDLE_TIP, [2, 2, 6], [2, 4, 2]),
    ]

    max_abs_error = 0
    for seq_idx in range(10):
        deltas = [seq_idx * 3 + 0, seq_idx * 3 + 1, seq_idx * 3 + 2]
        words = touch.pack_timed_simultaneous_frame(frame_id=seq_idx, contacts=contacts, deltas_ms=deltas)
        meta, decoded = touch.unpack_timed_simultaneous_frame(words)

        assert meta["cooccurrence_preserved"] is True
        assert len(decoded) == len(contacts)

        encoded_order = [(deltas[i], contacts[i].region) for i in range(len(contacts))]
        decoded_order = [(decoded[i][0], decoded[i][1].region) for i in range(len(decoded))]
        assert decoded_order == encoded_order

        for expected, observed in zip(deltas, [pair[0] for pair in decoded]):
            max_abs_error = max(max_abs_error, abs(expected - observed))

    assert max_abs_error <= 1

    words = touch.pack_timed_simultaneous_frame(frame_id=5, contacts=contacts, deltas_ms=[1, 2, 3])
    flat_word_count = len(touch.pack_touch_strokes(contacts))
    timestamp_word_count = len(words) - 1 - flat_word_count
    assert timestamp_word_count == 2 * len(contacts)


def test_touch_proprioception_and_raii_complete_roundtrip() -> None:
    samples = [
        touch.ProprioSample(joint=touch.JointID.NECK, angle_deg=12.0, tension_level=1),
        touch.ProprioSample(joint=touch.JointID.LEFT_SHOULDER, angle_deg=25.0, tension_level=1),
        touch.ProprioSample(joint=touch.JointID.RIGHT_SHOULDER, angle_deg=28.0, tension_level=1),
        touch.ProprioSample(joint=touch.JointID.LEFT_ELBOW, angle_deg=40.0, tension_level=2),
        touch.ProprioSample(joint=touch.JointID.RIGHT_ELBOW, angle_deg=42.0, tension_level=2),
        touch.ProprioSample(joint=touch.JointID.LEFT_WRIST, angle_deg=18.0, tension_level=1),
        touch.ProprioSample(joint=touch.JointID.RIGHT_WRIST, angle_deg=20.0, tension_level=1),
        touch.ProprioSample(joint=touch.JointID.LEFT_HIP, angle_deg=55.0, tension_level=2),
        touch.ProprioSample(joint=touch.JointID.RIGHT_HIP, angle_deg=53.0, tension_level=2),
        touch.ProprioSample(joint=touch.JointID.LEFT_KNEE, angle_deg=70.0, tension_level=3),
        touch.ProprioSample(joint=touch.JointID.RIGHT_KNEE, angle_deg=68.0, tension_level=3),
        touch.ProprioSample(joint=touch.JointID.LEFT_ANKLE, angle_deg=22.0, tension_level=1),
        touch.ProprioSample(joint=touch.JointID.RIGHT_ANKLE, angle_deg=21.0, tension_level=1),
        touch.ProprioSample(joint=touch.JointID.SPINE, angle_deg=15.0, tension_level=2),
    ]

    words = touch.pack_proprioception_samples(samples)
    decoded = touch.unpack_proprioception_samples(words)

    assert len(decoded) == 14
    assert [sample.joint for sample in decoded] == [sample.joint for sample in samples]
    assert touch.max_angle_error(samples, decoded) <= 2.0

    cases = [
        (touch.BodyRegion.INDEX_TIP, touch.RAIIDescriptor(frequency_band=0, amplitude=1, envelope=0)),
        (touch.BodyRegion.PALM_CENTER, touch.RAIIDescriptor(frequency_band=2, amplitude=3, envelope=1)),
        (touch.BodyRegion.THUMB_TIP, touch.RAIIDescriptor(frequency_band=4, amplitude=5, envelope=2)),
        (touch.BodyRegion.MIDDLE_TIP, touch.RAIIDescriptor(frequency_band=6, amplitude=7, envelope=3)),
        (touch.BodyRegion.RING_TIP, touch.RAIIDescriptor(frequency_band=8, amplitude=9, envelope=4)),
        (touch.BodyRegion.PINKY_TIP, touch.RAIIDescriptor(frequency_band=10, amplitude=11, envelope=5)),
        (touch.BodyRegion.WRIST_FOREARM, touch.RAIIDescriptor(frequency_band=12, amplitude=13, envelope=6)),
        (touch.BodyRegion.FOOT_SOLE, touch.RAIIDescriptor(frequency_band=15, amplitude=14, envelope=7)),
    ]

    raii_words: list[int] = []
    for region, descriptor in cases:
        raii_words.extend(touch.pack_raii_complete(region=region, descriptor=descriptor))
    assert touch.unpack_raii_complete(raii_words) == cases


def test_touch_phase5_and_receptor_model_paths() -> None:
    frame = p5.SimultaneousFrame(
        frame_id=3,
        contacts=[
            _make_stroke(touch.ReceptorType.SA_I, touch.BodyRegion.THUMB_TIP, [2, 2, 6], [3, 5, 3]),
            _make_stroke(touch.ReceptorType.SA_I, touch.BodyRegion.INDEX_TIP, [2, 2, 6], [3, 5, 3]),
            _make_stroke(touch.ReceptorType.SA_I, touch.BodyRegion.MIDDLE_TIP, [2, 2, 6], [3, 5, 3]),
        ],
    )
    frame_words = p5.pack_simultaneous_frame(frame)
    frame_meta, decoded_frame = p5.unpack_simultaneous_frame(frame_words)
    assert frame_meta["cooccurrence_preserved"] is True
    assert len(decoded_frame.contacts) == 3

    raii_words = p5.pack_raii_frequency_sequence(touch.BodyRegion.INDEX_TIP, [1, 5, 9, 15])
    decoded_raii = p5.unpack_raii_frequency_words(raii_words)
    assert [sample.band for sample in decoded_raii] == [1, 5, 9, 15]
    assert [sample.region for sample in decoded_raii] == [touch.BodyRegion.INDEX_TIP] * 4

    base_stroke = _make_stroke(
        receptor=touch.ReceptorType.SA_I,
        region=touch.BodyRegion.INDEX_TIP,
        directions=[0, 2, 4],
        pressures=[3, 4, 3],
    )
    offsets = [(-1, 0), (0, 0), (1, 0)]
    anchors: list[tuple[int, int]] = []
    streams: list[tuple[int, ...]] = []
    for offset in offsets:
        words = p5.pack_anchored_touch(base_stroke, offset=offset)
        meta, decoded = p5.unpack_anchored_touch(words)
        assert meta["decoded"] is True
        assert decoded is not None
        assert decoded.region == touch.BodyRegion.INDEX_TIP
        streams.append(tuple(words))
        anchors.append(decoded.anchor)
    assert len(set(streams)) == 3
    assert len(set(anchors)) == 3

    contour = rmodel.build_contour_following_trace(region=touch.BodyRegion.PALM_CENTER, loops=1)
    contour_directions = [cmd.direction for cmd in contour.commands if isinstance(cmd, touch.DrawDir)]
    assert len(contour_directions) >= 8
    assert len(set(contour_directions)) >= 2
    assert len(contour.pressure_profile) == len(contour_directions)

    press = rmodel.build_press_release_trace(region=touch.BodyRegion.INDEX_TIP, peak_pressure=7, ascent_steps=4)
    press_directions = [cmd.direction for cmd in press.commands if isinstance(cmd, touch.DrawDir)]
    assert 2 in press_directions and 6 in press_directions
    assert set(rmodel.receptor_ids()) == {0, 1, 2, 3}

    patterns = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    roundtrip_ok = 0
    for pattern in patterns:
        stroke = _make_stroke(
            receptor=touch.ReceptorType[pattern["receptor"]],
            region=touch.BodyRegion[pattern["region"]],
            directions=list(pattern["directions"]),
            pressures=list(pattern["pressure_profile"]),
        )
        words = touch.pack_touch_strokes([stroke])
        _, decoded = touch.unpack_touch_words(words)
        if (
            decoded
            and decoded[0].receptor == touch.ReceptorType[pattern["receptor"]]
            and decoded[0].region == touch.BodyRegion[pattern["region"]]
            and _dirs(decoded[0]) == list(pattern["directions"])
            and decoded[0].pressure_profile == list(pattern["pressure_profile"])
        ):
            roundtrip_ok += 1
    assert roundtrip_ok == len(patterns)
