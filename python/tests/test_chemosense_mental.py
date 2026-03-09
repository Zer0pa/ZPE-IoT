from __future__ import annotations

import json
import random
from pathlib import Path

from zpe_iot.chemosense import mental

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "clinical_phosphenes.json"


def _draw_dirs(stroke: mental.MentalStroke) -> list[int]:
    return [cmd.direction for cmd in stroke.commands if isinstance(cmd, mental.DrawDir)]


def _angle(direction: int, profile: mental.DirectionProfile) -> float:
    if profile == mental.DirectionProfile.D6_12:
        return float(direction * 30)
    return float(direction * 45)


def _angular_error(a: float, b: float) -> float:
    return abs(((a - b + 180.0) % 360.0) - 180.0)


def _mutate_words(words: list[int], mutation_idx: int) -> list[int]:
    data = list(words)
    if not data:
        return []
    mod = mutation_idx % 12
    if mod == 0 and len(data) >= 1:
        return data[1:]
    if mod == 1 and len(data) >= 2:
        data[0], data[1] = data[1], data[0]
        return data
    if mod == 2 and len(data) >= 3:
        return data[:2] + data[3:]
    if mod == 3 and len(data) >= 4:
        return data[:3] + data[4:]
    if mod == 4 and len(data) >= 5:
        return data[:4]
    if mod == 5 and len(data) >= 2:
        data.insert(1, (3 << 18) | 0x8000)
        return data
    if mod == 6 and len(data) >= 1:
        data[0] = data[0] ^ (1 << 18)
        return data
    if mod == 7 and len(data) >= 5:
        data[4] = (2 << 18) | 0x0100 | (0xF << 4)
        return data
    if mod == 8 and len(data) >= 5:
        data[4] = data[4] & (~0x0100)
        return data
    if mod == 9 and len(data) >= 6:
        data[4], data[5] = data[5], data[4]
        return data
    if mod == 10 and len(data) >= 4:
        data[3] = (data[3] & (~0x0FFF)) | 0x0100 | 255
        return data
    if mod == 11 and len(data) >= 1:
        return [data[0] ^ (1 << 5)] + data[1:]
    return data


def _non_mental_burst(type_bit: int, *, length: int = 12) -> list[int]:
    out: list[int] = []
    for i in range(length):
        mode = 2 if i % 2 == 0 else 3
        version = i % 4
        payload = type_bit | ((i & 0xF) << 2)
        out.append((mode << 18) | (version << 16) | payload)
    return out


def test_mental_pack_unpack_rle_raw_and_temporal_metadata() -> None:
    stroke = mental.MentalStroke(
        commands=[mental.MoveTo(12, 34)] + [mental.DrawDir(0)] * 20 + [mental.DrawDir(4)] * 16,
        form_class=mental.FormClass.TUNNEL,
        symmetry=mental.SymmetryOrder.D4,
        direction_profile=mental.DirectionProfile.COMPASS_8,
        spatial_frequency=3,
        drift_speed=1,
        frame_index=7,
        delta_ms=99,
    )

    raw_words = mental.pack_mental_strokes([stroke], metadata={"use_rle": False})
    rle_words = mental.pack_mental_strokes([stroke])

    raw_meta, raw_decoded = mental.unpack_mental_words(raw_words)
    rle_meta, rle_decoded = mental.unpack_mental_words_rle(rle_words)

    assert raw_meta is not None
    assert rle_meta is not None
    assert raw_meta["stroke_count"] == 1
    assert rle_meta["stroke_count"] == 1
    assert rle_meta["encoding"] in {"rle", "mixed"}
    assert len(rle_words) <= len(raw_words)

    assert raw_decoded[0].frame_index == 7
    assert raw_decoded[0].delta_ms == 99
    assert rle_decoded[0].frame_index == 7
    assert rle_decoded[0].delta_ms == 99
    assert _draw_dirs(raw_decoded[0]) == _draw_dirs(stroke)
    assert _draw_dirs(rle_decoded[0]) == _draw_dirs(stroke)


def test_mental_type_bit_collisions_and_determinism() -> None:
    stroke = mental.MentalStroke(
        commands=[mental.MoveTo(0, 0), mental.DrawDir(7)],
        form_class=mental.FormClass.COBWEB,
        symmetry=mental.SymmetryOrder.D4,
    )
    words_a = mental.pack_mental_strokes([stroke])
    words_b = mental.pack_mental_strokes([stroke])

    assert words_a == words_b
    assert len(words_a) > 0
    assert all((w & 0x0100) != 0 for w in words_a)
    assert all((w & 0x8000) == 0 for w in words_a)
    assert all((w & 0x4000) == 0 for w in words_a)
    assert all((w & 0x2000) == 0 for w in words_a)
    assert all((w & 0x1000) == 0 for w in words_a)


def test_mental_form_constants_and_symmetry_paths() -> None:
    fixtures = [
        mental.generate_tunnel(center=(128, 128), radius=32),
        mental.generate_spiral(center=(128, 128), turns=3),
        mental.generate_lattice(origin=(120, 120), spacing=2, rows=4, cols=5),
        mental.generate_cobweb(center=(128, 128), branches=4, depth=3),
    ]

    for strokes in fixtures:
        words = mental.pack_mental_strokes(strokes)
        _, recovered = mental.unpack_mental_words(words)
        assert len(recovered) == len(strokes)
        for stroke in recovered:
            assert any(isinstance(cmd, mental.DrawDir) for cmd in stroke.commands)

    dirs = [0, 2, 4, 6]
    copies = mental.apply_symmetry(dirs, mental.SymmetryOrder.D4, profile=mental.DirectionProfile.COMPASS_8)
    assert len(copies) == 4
    assert mental.verify_symmetry([d for copy in copies for d in copy], mental.SymmetryOrder.D4) is True


def test_mental_ingest_fixture_thresholds() -> None:
    entries = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    results = mental.ingest_clinical_dataset(entries)

    correct = 0
    seen_kluver: set[str] = set()
    expected_by_kluver = {
        "I": mental.FormClass.TUNNEL,
        "II": mental.FormClass.SPIRAL,
        "III": mental.FormClass.LATTICE,
        "IV": mental.FormClass.COBWEB,
    }

    for entry, result in zip(entries, results):
        words = mental.pack_mental_strokes([result.stroke])
        _meta, recovered = mental.unpack_mental_words(words)
        assert len(recovered) == 1

        expected = entry.get("expected_form_class")
        if expected is None:
            if result.used_fallback:
                correct += 1
        elif recovered[0].form_class.name == expected:
            correct += 1

        kclass = entry.get("kluver_class")
        if kclass is not None:
            seen_kluver.add(str(kclass))
            assert result.stroke.form_class == expected_by_kluver[str(kclass)]

    assert correct >= 16
    assert seen_kluver == {"I", "II", "III", "IV"}


def test_mental_d6_exact_and_profile_coexistence() -> None:
    max_error = 0.0
    for base in range(6):
        expected_dirs = mental.apply_symmetry(
            [base],
            mental.SymmetryOrder.D6,
            profile=mental.DirectionProfile.D6_12,
        )
        expected = [seq[0] for seq in expected_dirs]

        stroke = mental.MentalStroke(
            commands=[mental.MoveTo(100, 100)]
            + [mental.DrawDir(d, profile=mental.DirectionProfile.D6_12) for d in expected],
            form_class=mental.FormClass.SPIRAL,
            symmetry=mental.SymmetryOrder.D6,
            direction_profile=mental.DirectionProfile.D6_12,
            spatial_frequency=3,
            drift_speed=1,
        )

        words = mental.pack_mental_strokes([stroke])
        _meta, recovered = mental.unpack_mental_words(words)

        assert len(recovered) == 1
        got = _draw_dirs(recovered[0])
        assert got == expected

        for exp_d, got_d in zip(expected, got):
            err = _angular_error(
                _angle(exp_d, mental.DirectionProfile.D6_12),
                _angle(got_d, mental.DirectionProfile.D6_12),
            )
            max_error = max(max_error, err)

    stroke_8 = mental.MentalStroke(
        commands=[mental.MoveTo(10, 10), mental.DrawDir(4), mental.DrawDir(6)],
        form_class=mental.FormClass.LATTICE,
        symmetry=mental.SymmetryOrder.D2,
        direction_profile=mental.DirectionProfile.COMPASS_8,
        spatial_frequency=2,
        drift_speed=1,
    )
    stroke_12 = mental.MentalStroke(
        commands=[mental.MoveTo(20, 20)]
        + [mental.DrawDir(d, profile=mental.DirectionProfile.D6_12) for d in [0, 2, 4, 6, 8, 10]],
        form_class=mental.FormClass.SPIRAL,
        symmetry=mental.SymmetryOrder.D6,
        direction_profile=mental.DirectionProfile.D6_12,
        spatial_frequency=2,
        drift_speed=1,
    )

    words = mental.pack_mental_strokes([stroke_8]) + mental.pack_mental_strokes([stroke_12])
    _meta, recovered = mental.unpack_mental_words(words)
    assert len(recovered) == 2
    assert recovered[0].direction_profile == mental.DirectionProfile.COMPASS_8
    assert recovered[1].direction_profile == mental.DirectionProfile.D6_12
    assert max_error == 0.0


def test_mental_malformed_and_contamination_no_false_positives() -> None:
    rng = random.Random(260218)
    valid_words: list[list[int]] = []

    for case_idx in range(40):
        profile = mental.DirectionProfile.COMPASS_8 if case_idx % 2 == 0 else mental.DirectionProfile.D6_12
        max_dir = 7 if profile == mental.DirectionProfile.COMPASS_8 else 11
        directions = [rng.randint(0, max_dir) for _ in range(6)]
        stroke = mental.MentalStroke(
            commands=[mental.MoveTo(64 + case_idx, 64 + case_idx)]
            + [mental.DrawDir(d, profile=profile) for d in directions],
            form_class=mental.FormClass(case_idx % 4),
            symmetry=mental.SymmetryOrder.D6 if profile == mental.DirectionProfile.D6_12 else mental.SymmetryOrder.D4,
            direction_profile=profile,
            spatial_frequency=case_idx % 8,
            drift_speed=case_idx % 4,
            frame_index=case_idx % 16,
            delta_ms=(case_idx * 17) % 256,
        )
        valid_words.append(mental.pack_mental_strokes([stroke]))

    for idx, words in enumerate(valid_words):
        mutated = _mutate_words(words, idx)
        # Must never crash on malformed sequences.
        _meta, _decoded = mental.unpack_mental_words(mutated)

    contamination_bits = [0x8000, 0x4000, 0x2000, 0x1000, 0x0800, 0x0400, 0x0200]
    false_positives = 0

    for bit in contamination_bits:
        burst = _non_mental_burst(bit, length=18)
        _meta, recovered = mental.unpack_mental_words(burst)
        if recovered:
            false_positives += 1

        mental_anchor = valid_words[0]
        mixed = burst[:6] + mental_anchor + burst[6:]
        _meta, recovered_mixed = mental.unpack_mental_words(mixed)
        if len(recovered_mixed) != 1:
            false_positives += 1

    assert false_positives == 0
