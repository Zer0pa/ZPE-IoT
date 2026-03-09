from __future__ import annotations

import pytest

from zpe_iot.chemosense.common import quantize as qz
from zpe_iot.chemosense.smell import adaptation as sadapt
from zpe_iot.chemosense.smell import codec as scodec
from zpe_iot.chemosense.smell import molecular_bridge as smol
from zpe_iot.chemosense.smell import odor_space as sspace
from zpe_iot.chemosense.smell import pack as spack
from zpe_iot.chemosense.smell import phase5_augment as sphase
from zpe_iot.chemosense.smell import types as stypes
from zpe_iot.chemosense import touch as tmod
from zpe_iot.chemosense.taste import codec as tcodec
from zpe_iot.chemosense.taste import fusion_scheduler as tfusion
from zpe_iot.chemosense.taste import pack as tpack
from zpe_iot.chemosense.taste import taste_space as tspace
from zpe_iot.chemosense.taste import temporal_codebook as tcode
from zpe_iot.chemosense.taste import types as ttypes


def _touch_packet(seed: int) -> list[int]:
    stroke = tmod.TouchStroke(
        commands=[
            tmod.MoveTo(0, 0),
            tmod.DrawDir((int(seed) * 3 + 1) % 8),
            tmod.DrawDir((int(seed) * 3 + 2) % 8),
        ],
        receptor=tmod.ReceptorType.SA_I,
        region=tmod.BodyRegion.INDEX_TIP,
        pressure_profile=[2, 3],
    )
    return tmod.pack_touch_strokes([stroke])


def test_quantize_pipeline_and_unknown_command_error() -> None:
    polylines = [
        qz.PolylineShape(points=[(0.2, 0.1), (1.7, 0.9), (1.7, 0.9), (2.2, 1.8)], stroke="red"),
        qz.PolylineShape(points=[(1.0, 1.0)], stroke="drop"),
    ]
    quantized = qz.quantize_polylines(polylines)
    assert len(quantized) == 1

    paths = qz.polylines_to_strokes(quantized)
    assert len(paths) == 1
    assert isinstance(paths[0].commands[0], qz.MoveTo)

    rebuilt = qz.strokes_to_polylines(paths)
    assert rebuilt[0].points[0] == (0, 0)

    multi = qz.StrokePath(commands=[qz.MoveTo(0, 0), qz.DrawDir(0), qz.MoveTo(2, 2), qz.DrawDir(4)])
    split = qz.strokes_to_polylines([multi])
    assert len(split) == 2

    bad = qz.StrokePath(commands=[qz.MoveTo(0, 0), object()])
    with pytest.raises(TypeError):
        qz.strokes_to_polylines([bad])


def test_smell_adaptation_codec_and_pack_paths() -> None:
    params = sadapt.AdaptationParams(half_life=4, floor=3)
    encoded = sadapt.encode_adaptation_params(params)
    decoded = sadapt.decode_adaptation_params(encoded)
    assert decoded == params
    assert sadapt.apply_adaptation(7, 0, params) == 7
    assert 0 <= sadapt.apply_adaptation(7, 5, params) <= 7

    with pytest.raises(ValueError):
        sadapt.apply_adaptation(-1, 1, params)
    with pytest.raises(ValueError):
        sadapt.apply_adaptation(1, -1, params)
    with pytest.raises(ValueError):
        sadapt.AdaptationParams(half_life=16, floor=0)

    events = sspace.synthetic_sniff_events(stypes.OdorCategory.FRUITY)
    stroke = scodec.events_to_stroke(events)
    decoded_events = scodec.stroke_to_events(stroke)
    assert len(decoded_events) == len(events)

    words = scodec.encode_smell_strokes([stroke], metadata={"sniff_hz": 4})
    metadata, strokes = scodec.decode_smell_words(words)
    assert metadata == {"sniff_hz": 4}
    assert len(strokes) == 1

    with pytest.raises(ValueError):
        scodec.events_to_stroke([])

    with pytest.raises(ValueError):
        spack.pack_odor_strokes([stroke], metadata={"sniff_hz": 64})

    long_stroke = stypes.OdorStroke(
        commands=[qz.MoveTo(3, 3)] + [qz.DrawDir(0)] * 8,
        category=stypes.OdorCategory.FLORAL,
        pleasantness_start=3,
        intensity_start=4,
    )
    with pytest.raises(ValueError):
        spack.pack_odor_strokes([long_stroke])

    class DummyStroke:
        commands = [qz.DrawDir(0)]
        category = stypes.OdorCategory.FLORAL
        pleasantness_start = 0
        intensity_start = 0

    with pytest.raises(ValueError):
        spack.pack_odor_strokes([DummyStroke()])

    noisy_meta, noisy_strokes = spack.unpack_odor_words(["x", 0x12345, *words, None])  # type: ignore[list-item]
    assert noisy_meta == {"sniff_hz": 4}
    assert len(noisy_strokes) == 1


def test_smell_space_bridge_and_phase5_augment() -> None:
    anchor = sspace.category_anchor(stypes.OdorCategory.SPICY_HERBAL)
    assert len(anchor) == 2
    assert sspace.project_quality_vector_to_pom([0.2, 0.8, 0.1, 0.2, 0.0])[0] in range(8)
    assert sspace.project_odor_vector3_to_pom([0.4, 0.5, 0.3])[1] in range(8)
    assert sspace.nearest_direction_step((3, 3), (4, 2)) in range(8)
    assert sspace.apply_direction((4, 4), 0) == (5, 4)

    with pytest.raises(ValueError):
        sspace.category_anchor(1)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        sspace.project_quality_vector_to_pom([0.1, 0.2])
    with pytest.raises(ValueError):
        sspace.project_odor_vector3_to_pom([0.1, 0.2])
    with pytest.raises(ValueError):
        sspace.apply_direction((1, 1), 9)

    assert 0.0 <= smol.descriptor_complexity_hint(140, ["ester", "aromatic"]) <= 1.0
    assert len(smol.descriptor_to_tree_ops(88.0, 8.5, ["ester"])) == 3
    fallback = (0, 1, 2)
    assert smol.descriptor_to_tree_ops_safe(None, fallback) == fallback
    assert smol.descriptor_to_tree_ops_safe({"molecular_weight": 0, "vapor_pressure_kpa": 0, "functional_groups": []}, fallback) == fallback

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

    record = sphase.profile_to_augmented_record(profile)
    vector_record = sphase.vector3_to_augmented_record([0.6, 0.5, 0.4], category=stypes.OdorCategory.WOODY_EARTHY)
    assert record.stroke.category == stypes.OdorCategory.FRUITY
    assert vector_record.stroke.category == stypes.OdorCategory.WOODY_EARTHY

    packed = sphase.pack_augmented_records([record, vector_record])
    unpacked = sphase.unpack_augmented_words(packed)
    assert len(unpacked) == 2
    assert sphase.augmented_signature(unpacked[0]) == sphase.augmented_signature(record)
    assert len(sphase.direction_sequence(record)) >= 1

    episode = sphase.pack_z_episode(
        [record],
        z_level=stypes.SmellZLevel.EPISODIC,
        adaptation=sadapt.AdaptationParams(half_life=2, floor=3),
    )
    z_level, adaptation, restored = sphase.unpack_z_episode(episode)
    assert z_level == stypes.SmellZLevel.EPISODIC
    assert adaptation is not None
    assert len(restored) == 1
    assert len(sphase.unpack_instant_layer(episode)) == 1

    sig = sphase.ablation_signature(profile, tree_depth=3, complexity_bits=4, pom_resolution=8)
    assert len(sig) >= 10
    assert sphase.estimated_bits_per_event(tree_depth=3, complexity_bits=4) == 10

    with pytest.raises(ValueError):
        sphase.profile_to_augmented_record({"category": "FRUITY", "quality": [0.1, 0.2]})
    with pytest.raises(TypeError):
        sphase.pack_z_episode([record], z_level=0)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        sphase.pack_z_episode([], z_level=stypes.SmellZLevel.INSTANT)
    with pytest.raises(ValueError):
        sphase.pack_z_episode([record] * 5, z_level=stypes.SmellZLevel.INSTANT)
    with pytest.raises(ValueError):
        sphase.estimated_bits_per_event(tree_depth=0, complexity_bits=4)


def test_taste_temporal_codebook_and_types() -> None:
    coarse = tcode.encode_temporal_coarse((0, 2, 4, 6, 0, 2, 4, 6))
    assert tcode.decode_temporal_coarse(*coarse) == (0, 2, 4, 6, 0, 2, 4, 6)

    fine = tcode.encode_temporal_fine((1, 1, 0, 0, 0, 7, 6, 6))
    assert tcode.decode_temporal_fine(*fine) == (1, 1, 0, 0, 0, 7, 6, 6)
    assert tcode.auto_select_resolution((0, 2, 4, 6, 0, 2, 4, 6)) == tcode.COARSE_MODE
    assert tcode.auto_select_resolution((1, 1, 0, 0, 0, 7, 6, 6)) == tcode.FINE_MODE

    with pytest.raises(ValueError):
        tcode.encode_temporal_coarse((1, 2, 4, 6, 0, 2, 4, 6))
    with pytest.raises(ValueError):
        tcode.encode_temporal_fine((0, 1, 2))

    with pytest.raises(ValueError):
        ttypes.validate_quality_vector((1, 2, 3))

    stroke = ttypes.TasteStroke(
        commands=[qz.MoveTo(1, 1), qz.DrawDir(0), qz.DrawDir(2)],
        dominant_quality=ttypes.TasteQuality.SWEET,
        quality_vector=(7, 1, 1, 0, 3),
    )
    assert stroke.draw_count == 2
    assert stroke.directions() == [0, 2]

    with pytest.raises(ValueError):
        ttypes.TasteStroke(
            commands=[qz.DrawDir(0)],  # type: ignore[list-item]
            dominant_quality=ttypes.TasteQuality.SWEET,
            quality_vector=(7, 1, 1, 0, 3),
        )
    with pytest.raises(ValueError):
        ttypes.ZLayeredTasteEvent(
            dominant_quality=ttypes.TasteQuality.SWEET,
            secondary_quality=ttypes.TasteQuality.SOUR,
            intensity=3,
            intensity_direction=0,
            temporal_directions=(0, 2, 4),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("quality", list(ttypes.TasteQuality))
def test_taste_space_synthetic_and_projection_paths(quality: ttypes.TasteQuality) -> None:
    profiles = tspace.synthetic_quality_profiles()
    assert quality in profiles

    vector = profiles[quality]
    assert tspace.dominant_quality_from_vector(vector) in ttypes.TasteQuality
    assert tspace.secondary_quality_from_vector(vector) in ttypes.TasteQuality
    assert tspace.dominant_intensity_from_vector(vector) in range(8)
    assert tspace.project_quality_vector_to_pca1(vector) >= 0.0
    assert tspace.project_quality_vector_to_pca2(vector)[0] in range(8)
    assert tspace.quality_vector_to_taste_time_point(vector, 3)[0] == 3
    assert tspace.quality_vector_to_taste_plane_point(vector)[0] in range(8)
    assert tspace.nearest_direction_step((1, 1), (1, 1)) == 0
    assert tspace.apply_direction((4, 4), 0) == (5, 4)
    assert len(tspace.trajectory_from_pca2(vector, phase_count=8)) == 8

    events4 = tspace.synthetic_taste_events(quality, phase_count=4)
    events8 = tspace.synthetic_taste_events(quality, phase_count=8)
    assert len(events4) == 4
    assert len(events8) == 8
    assert len(tspace.synthetic_taste_stroke(quality, phase_count=4).commands) == 5
    assert len(tspace.synthetic_taste_stroke_8phase(quality).commands) == 9

    z_event = tspace.zlayered_event_from_vector(
        quality_vector=vector,
        temporal_directions=(0, 2, 4, 6, 0, 2, 4, 6),
        intensity_end=3,
        flavor_link=(1, 2),
    )
    assert z_event.flavor_link == (1, 2)


def test_taste_space_error_paths() -> None:
    with pytest.raises(ValueError):
        tspace.trajectory_from_pca2((7, 1, 1, 0, 3), phase_count=0)
    with pytest.raises(ValueError):
        tspace.synthetic_taste_events(ttypes.TasteQuality.SWEET, phase_count=6)
    with pytest.raises(TypeError):
        tspace.synthetic_taste_events("sweet")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        tspace.apply_direction((1, 1), 8)
    with pytest.raises(ValueError):
        tspace.quality_vector_to_taste_time_point((1, 2, 3), 1)  # type: ignore[arg-type]


def test_taste_pack_codec_and_fusion_paths() -> None:
    stroke = tspace.synthetic_taste_stroke(ttypes.TasteQuality.SWEET)
    packed_strokes = tpack.pack_taste_strokes([stroke])
    metadata, unpacked_strokes = tpack.unpack_taste_words([*packed_strokes, "noise"])  # type: ignore[list-item]
    assert metadata is not None
    assert metadata["stroke_count"] == 1
    assert len(unpacked_strokes) == 1

    with pytest.raises(TypeError):
        tpack.pack_taste_strokes([object()])  # type: ignore[list-item]

    class DummyTaste:
        commands = [qz.DrawDir(0)]
        dominant_quality = ttypes.TasteQuality.SWEET
        quality_vector = (7, 1, 1, 0, 3)

    with pytest.raises(TypeError):
        tpack.pack_taste_strokes([DummyTaste()])  # type: ignore[list-item]

    event_fine = ttypes.ZLayeredTasteEvent(
        dominant_quality=ttypes.TasteQuality.SWEET,
        secondary_quality=ttypes.TasteQuality.UMAMI,
        intensity=6,
        intensity_direction=2,
        temporal_directions=(1, 1, 0, 0, 0, 7, 6, 6),
        duration=ttypes.DurationClass.LONG,
        flavor_link=(1, 2),
    )
    event_coarse = ttypes.ZLayeredTasteEvent(
        dominant_quality=ttypes.TasteQuality.SOUR,
        secondary_quality=ttypes.TasteQuality.SALT,
        intensity=3,
        intensity_direction=6,
        temporal_directions=(0, 2, 4, 6, 0, 2, 4, 6),
        duration=ttypes.DurationClass.SHORT,
    )

    z_words = tpack.pack_taste_zlayered([event_fine, event_coarse], adaptive=True)
    z_meta, z_events = tpack.unpack_taste_zlayered(z_words)
    assert z_meta is not None
    assert z_meta["event_count"] == 2
    assert len(z_events) == 2

    quality_layer = tpack.decode_zlayer_words(z_words, ttypes.TasteZLevel.QUALITY)
    assert len(quality_layer) == 2

    with pytest.raises(TypeError):
        tpack.pack_taste_zlevel_word(0, 12)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        tpack.pack_taste_zlevel_word(ttypes.TasteZLevel.QUALITY, 999)
    with pytest.raises(TypeError):
        tpack.decode_zlayer_words(z_words, 0)  # type: ignore[arg-type]

    assert tpack.unpack_taste_zlevel_word("bad") is None  # type: ignore[arg-type]

    wrapped_words = tcodec.encode_taste_strokes([stroke])
    _meta, _decoded = tcodec.decode_taste_words(wrapped_words)
    assert len(_decoded) == 1
    assert len(tcodec.encode_synthetic_quality_sequence([ttypes.TasteQuality.BITTER])) > 0

    profile = {
        "quality_vector": (7, 1, 1, 0, 3),
        "temporal_directions": (0, 2, 4, 6, 0, 2, 4, 6),
        "intensity_end": 2,
        "flavor_link": (1, 1),
    }
    assert len(tcodec.encode_real_taste_profile(profile, adaptive=True)) >= 4

    with pytest.raises(TypeError):
        tcodec.encode_real_taste_profile("bad")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        tcodec.encode_real_taste_profile({"quality_vector": (1, 2, 3, 4, 5)})

    smell_packets = [spack.pack_odor_strokes([sspace.synthetic_sniff_stroke(stypes.OdorCategory.FLORAL)])]
    touch_packets = [_touch_packet(0)]
    fused = tpack.pack_fused_multimodal([event_coarse], smell_packets, touch_packets, adaptive=True)
    scheduler = tfusion.FusionScheduler()
    stats = scheduler.ingest_stream([0x123456, *fused, 0x111111])
    assert stats["total_words"] >= len(fused)
    fused_events = scheduler.fuse_zlayer_events()
    assert len(fused_events) == 1
    assert len(scheduler.emit_fused_words()) > 0
