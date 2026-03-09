from __future__ import annotations

from zpe_iot.chemosense import mental, smell, taste, touch


def _touch_packet(seed: int) -> list[int]:
    stroke = touch.TouchStroke(
        commands=[
            touch.MoveTo(0, 0),
            touch.DrawDir((int(seed) * 2) % 8),
            touch.DrawDir((int(seed) * 2 + 1) % 8),
        ],
        receptor=touch.ReceptorType.SA_I,
        region=touch.BodyRegion.INDEX_TIP,
        pressure_profile=[2, 3],
    )
    return touch.pack_touch_strokes([stroke])


def test_smell_roundtrip_metadata_and_category() -> None:
    strokes = [
        smell.synthetic_sniff_stroke(smell.OdorCategory.FLORAL),
        smell.synthetic_sniff_stroke(smell.OdorCategory.WOODY_EARTHY),
    ]

    words = smell.encode_smell_strokes(strokes, metadata={"sniff_hz": 3})
    metadata, decoded = smell.decode_smell_words(words)

    assert metadata == {"sniff_hz": 3}
    assert len(decoded) == len(strokes)
    assert [stroke.category for stroke in decoded] == [stroke.category for stroke in strokes]
    assert [len(stroke.commands) for stroke in decoded] == [len(stroke.commands) for stroke in strokes]


def test_smell_augmented_episode_roundtrip_signature() -> None:
    profile = {
        "name": "ethyl acetate",
        "category": "FRUITY",
        "quality": [0.15, 0.85, 0.05, 0.05, 0.10],
        "complexity": 0.35,
        "chirality": "ACHIRAL",
        "molecular_descriptors": {
            "molecular_weight": 88.11,
            "vapor_pressure_kpa": 13.3,
            "functional_groups": ["ester"],
        },
    }
    record = smell.profile_to_augmented_record(profile)
    words = smell.pack_z_episode([record], z_level=smell.SmellZLevel.EPISODIC)

    z_level, adaptation, decoded = smell.unpack_z_episode(words)

    assert z_level == smell.SmellZLevel.EPISODIC
    assert adaptation is not None
    assert len(decoded) == 1
    assert smell.augmented_signature(decoded[0]) == smell.augmented_signature(record)


def test_taste_zlayer_roundtrip() -> None:
    event = taste.zlayered_event_from_vector(
        quality_vector=(7, 1, 1, 0, 3),
        temporal_directions=(1, 1, 0, 0, 0, 7, 6, 6),
        intensity_end=4,
    )
    words = taste.pack_taste_zlayered([event], adaptive=True)
    metadata, decoded = taste.unpack_taste_zlayered(words)

    assert metadata is not None
    assert metadata["event_count"] == 1
    assert decoded[0].dominant_quality == event.dominant_quality
    assert decoded[0].secondary_quality == event.secondary_quality
    assert decoded[0].intensity == event.intensity
    assert decoded[0].temporal_directions == event.temporal_directions


def test_fusion_scheduler_builds_deterministic_frames() -> None:
    taste_events = [
        taste.zlayered_event_from_vector((7, 1, 1, 0, 3), temporal_directions=(0, 2, 4, 6, 0, 2, 4, 6)),
        taste.zlayered_event_from_vector((1, 7, 2, 1, 1), temporal_directions=(0, 2, 4, 6, 0, 2, 4, 6)),
    ]
    smell_packets = [
        smell.encode_smell_strokes([smell.synthetic_sniff_stroke(smell.OdorCategory.FLORAL)]),
        smell.encode_smell_strokes([smell.synthetic_sniff_stroke(smell.OdorCategory.FRUITY)]),
    ]
    touch_packets = [_touch_packet(0), _touch_packet(1)]

    fused_words = taste.pack_fused_multimodal(
        taste_events=taste_events,
        smell_packets=smell_packets,
        touch_packets=touch_packets,
        adaptive=True,
    )
    scheduler = taste.FusionScheduler()
    ingest = scheduler.ingest_stream(fused_words)
    events = scheduler.fuse_zlayer_events()

    assert ingest["taste_packets"] == 2
    assert ingest["smell_packets"] == 2
    assert ingest["touch_packets"] == 2
    assert len(events) == 2
    assert scheduler.emit_fused_words() == fused_words


def test_mental_rle_roundtrip() -> None:
    stroke = mental.MentalStroke(
        commands=[mental.MoveTo(10, 10)] + [mental.DrawDir(0)] * 12 + [mental.DrawDir(4)] * 8,
        form_class=mental.FormClass.TUNNEL,
        symmetry=mental.SymmetryOrder.D4,
        direction_profile=mental.DirectionProfile.COMPASS_8,
        spatial_frequency=3,
        drift_speed=1,
        frame_index=3,
        delta_ms=21,
    )
    words = mental.pack_mental_strokes([stroke])
    metadata, decoded = mental.unpack_mental_words(words)

    assert metadata is not None
    assert metadata["stroke_count"] == 1
    assert decoded[0].frame_index == 3
    assert decoded[0].delta_ms == 21
    assert [cmd.direction for cmd in decoded[0].commands if isinstance(cmd, mental.DrawDir)] == [
        0
    ] * 12 + [4] * 8
