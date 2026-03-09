from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from . import mental, smell, taste, touch
from .common.quantize import DrawDir as SmellDrawDir
from .common.quantize import MoveTo as SmellMoveTo


class ChemosenseError(RuntimeError):
    """Base class for chemosense contract errors."""


class ChemosenseSchemaError(ChemosenseError, ValueError):
    """Raised when payload schema validation fails."""


class ChemosensePacketError(ChemosenseError):
    """Raised when encoded packet words are invalid or undecodable."""


def _as_mapping(payload: Mapping[str, Any] | dict[str, Any], *, kind: str) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise ChemosenseSchemaError(f"{kind} payload must be a mapping")
    return payload


def _as_uint3(value: Any, *, field: str) -> int:
    if not isinstance(value, int):
        raise ChemosenseSchemaError(f"{field} must be int")
    if not 0 <= value <= 7:
        raise ChemosenseSchemaError(f"{field} must be in [0, 7]")
    return int(value)


def _as_uint3_sequence(value: Any, *, field: str, length: int) -> tuple[int, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise ChemosenseSchemaError(f"{field} must be a sequence")
    if len(value) != length:
        raise ChemosenseSchemaError(f"{field} must have length {length}")
    return tuple(_as_uint3(v, field=f"{field}[{idx}]") for idx, v in enumerate(value))


def _as_words(words: Iterable[int], *, field: str) -> list[int]:
    try:
        out = [int(word) for word in words]
    except Exception as exc:  # pragma: no cover - defensive mapping
        raise ChemosensePacketError(f"{field} must be an iterable of ints") from exc
    if not out:
        raise ChemosensePacketError(f"{field} cannot be empty")
    return out


def _odor_category(value: Any) -> smell.OdorCategory:
    if isinstance(value, smell.OdorCategory):
        return value
    if isinstance(value, str):
        key = value.strip().upper()
        try:
            return smell.OdorCategory[key]
        except KeyError as exc:
            raise ChemosenseSchemaError(f"unknown smell category: {value}") from exc
    if isinstance(value, int):
        try:
            return smell.OdorCategory(value)
        except ValueError as exc:
            raise ChemosenseSchemaError(f"unknown smell category value: {value}") from exc
    raise ChemosenseSchemaError("smell category must be str|int|OdorCategory")


def _build_smell_stroke(item: Mapping[str, Any], idx: int) -> smell.OdorStroke:
    category = _odor_category(item.get("category", "FLORAL"))
    pleasantness_start = _as_uint3(item.get("pleasantness_start", 4), field=f"strokes[{idx}].pleasantness_start")
    intensity_start = _as_uint3(item.get("intensity_start", 0), field=f"strokes[{idx}].intensity_start")
    directions_raw = item.get("directions", ())
    if directions_raw is None:
        directions_raw = ()
    if isinstance(directions_raw, (str, bytes, bytearray)) or not isinstance(directions_raw, Sequence):
        raise ChemosenseSchemaError(f"strokes[{idx}].directions must be a sequence")
    directions = tuple(
        _as_uint3(direction, field=f"strokes[{idx}].directions[{jdx}]")
        for jdx, direction in enumerate(directions_raw)
    )

    commands: list[SmellMoveTo | SmellDrawDir] = [SmellMoveTo(pleasantness_start, 7 - intensity_start)]
    commands.extend(SmellDrawDir(direction) for direction in directions)

    try:
        return smell.OdorStroke(
            commands=commands,
            category=category,
            pleasantness_start=pleasantness_start,
            intensity_start=intensity_start,
        )
    except (TypeError, ValueError) as exc:
        raise ChemosenseSchemaError(f"invalid smell stroke at index {idx}: {exc}") from exc


def _taste_event_payload_to_object(item: Mapping[str, Any], idx: int) -> taste.ZLayeredTasteEvent:
    quality_vector = _as_uint3_sequence(item.get("quality_vector"), field=f"events[{idx}].quality_vector", length=5)
    temporal = _as_uint3_sequence(item.get("temporal_directions"), field=f"events[{idx}].temporal_directions", length=8)

    intensity_end = item.get("intensity_end")
    if intensity_end is not None:
        intensity_end = _as_uint3(intensity_end, field=f"events[{idx}].intensity_end")

    flavor_link_raw = item.get("flavor_link")
    flavor_link: tuple[int, int] | None
    if flavor_link_raw is None:
        flavor_link = None
    else:
        link = _as_uint3_sequence(flavor_link_raw, field=f"events[{idx}].flavor_link", length=2)
        flavor_link = (link[0], link[1])

    try:
        return taste.zlayered_event_from_vector(
            quality_vector=quality_vector,
            temporal_directions=temporal,
            intensity_end=intensity_end,
            flavor_link=flavor_link,
        )
    except (TypeError, ValueError) as exc:
        raise ChemosenseSchemaError(f"invalid taste event at index {idx}: {exc}") from exc


def _touch_receptor(value: Any) -> touch.ReceptorType:
    if isinstance(value, touch.ReceptorType):
        return value
    if isinstance(value, str):
        key = value.strip().upper()
        try:
            return touch.ReceptorType[key]
        except KeyError as exc:
            raise ChemosenseSchemaError(f"unknown touch receptor: {value}") from exc
    if isinstance(value, int):
        try:
            return touch.ReceptorType(value)
        except ValueError as exc:
            raise ChemosenseSchemaError(f"unknown touch receptor value: {value}") from exc
    raise ChemosenseSchemaError("touch receptor must be str|int|ReceptorType")


def _touch_region(value: Any) -> touch.BodyRegion:
    if isinstance(value, touch.BodyRegion):
        return value
    if isinstance(value, str):
        key = value.strip().upper()
        try:
            return touch.BodyRegion[key]
        except KeyError as exc:
            raise ChemosenseSchemaError(f"unknown touch region: {value}") from exc
    if isinstance(value, int):
        try:
            return touch.BodyRegion(value)
        except ValueError as exc:
            raise ChemosenseSchemaError(f"unknown touch region value: {value}") from exc
    raise ChemosenseSchemaError("touch region must be str|int|BodyRegion")


def _build_touch_stroke(item: Mapping[str, Any], idx: int) -> touch.TouchStroke:
    receptor = _touch_receptor(item.get("receptor", "SA_I"))
    region = _touch_region(item.get("region", "INDEX_TIP"))

    directions_raw = item.get("directions")
    if isinstance(directions_raw, (str, bytes, bytearray)) or not isinstance(directions_raw, Sequence) or not directions_raw:
        raise ChemosenseSchemaError(f"strokes[{idx}].directions must be a non-empty sequence")
    directions = [_as_uint3(direction, field=f"strokes[{idx}].directions[{jdx}]") for jdx, direction in enumerate(directions_raw)]

    pressures_raw = item.get("pressure_profile", [])
    if isinstance(pressures_raw, (str, bytes, bytearray)) or not isinstance(pressures_raw, Sequence):
        raise ChemosenseSchemaError(f"strokes[{idx}].pressure_profile must be a sequence")
    pressures = [_as_uint3(pressure, field=f"strokes[{idx}].pressure_profile[{jdx}]") for jdx, pressure in enumerate(pressures_raw)]
    if len(pressures) > len(directions):
        raise ChemosenseSchemaError(f"strokes[{idx}].pressure_profile cannot exceed directions length")

    commands: list[touch.MoveTo | touch.DrawDir] = [touch.MoveTo(0, 0)]
    commands.extend(touch.DrawDir(direction) for direction in directions)

    try:
        return touch.TouchStroke(
            commands=commands,
            receptor=receptor,
            region=region,
            pressure_profile=pressures,
        )
    except (TypeError, ValueError) as exc:
        raise ChemosenseSchemaError(f"invalid touch stroke at index {idx}: {exc}") from exc


def _mental_form_class(value: Any) -> mental.FormClass:
    if isinstance(value, mental.FormClass):
        return value
    if isinstance(value, str):
        key = value.strip().upper()
        try:
            return mental.FormClass[key]
        except KeyError as exc:
            raise ChemosenseSchemaError(f"unknown mental form_class: {value}") from exc
    if isinstance(value, int):
        try:
            return mental.FormClass(value)
        except ValueError as exc:
            raise ChemosenseSchemaError(f"unknown mental form_class value: {value}") from exc
    raise ChemosenseSchemaError("mental form_class must be str|int|FormClass")


def _mental_symmetry(value: Any) -> mental.SymmetryOrder:
    if isinstance(value, mental.SymmetryOrder):
        return value
    if isinstance(value, str):
        key = value.strip().upper()
        try:
            return mental.SymmetryOrder[key]
        except KeyError as exc:
            raise ChemosenseSchemaError(f"unknown mental symmetry: {value}") from exc
    if isinstance(value, int):
        try:
            return mental.SymmetryOrder(value)
        except ValueError as exc:
            raise ChemosenseSchemaError(f"unknown mental symmetry value: {value}") from exc
    raise ChemosenseSchemaError("mental symmetry must be str|int|SymmetryOrder")


def _mental_profile(value: Any) -> mental.DirectionProfile:
    if isinstance(value, mental.DirectionProfile):
        return value
    if isinstance(value, str):
        key = value.strip().upper()
        try:
            return mental.DirectionProfile[key]
        except KeyError as exc:
            raise ChemosenseSchemaError(f"unknown mental direction_profile: {value}") from exc
    if isinstance(value, int):
        try:
            return mental.DirectionProfile(value)
        except ValueError as exc:
            raise ChemosenseSchemaError(f"unknown mental direction_profile value: {value}") from exc
    raise ChemosenseSchemaError("mental direction_profile must be str|int|DirectionProfile")


def _build_mental_stroke(item: Mapping[str, Any], idx: int) -> mental.MentalStroke:
    form_class = _mental_form_class(item.get("form_class", "SPIRAL"))
    symmetry = _mental_symmetry(item.get("symmetry", "D4"))
    direction_profile = _mental_profile(item.get("direction_profile", "COMPASS_8"))

    start_raw = item.get("start", [0, 0])
    if isinstance(start_raw, (str, bytes, bytearray)) or not isinstance(start_raw, Sequence) or len(start_raw) != 2:
        raise ChemosenseSchemaError(f"strokes[{idx}].start must be a 2-item sequence")
    if not all(isinstance(v, int) for v in start_raw):
        raise ChemosenseSchemaError(f"strokes[{idx}].start values must be ints")
    start_x = int(start_raw[0])
    start_y = int(start_raw[1])

    directions_raw = item.get("directions")
    if isinstance(directions_raw, (str, bytes, bytearray)) or not isinstance(directions_raw, Sequence) or not directions_raw:
        raise ChemosenseSchemaError(f"strokes[{idx}].directions must be a non-empty sequence")
    modulus = mental.direction_modulus(direction_profile)
    directions: list[int] = []
    for jdx, direction in enumerate(directions_raw):
        if not isinstance(direction, int):
            raise ChemosenseSchemaError(f"strokes[{idx}].directions[{jdx}] must be int")
        if not 0 <= int(direction) < modulus:
            raise ChemosenseSchemaError(
                f"strokes[{idx}].directions[{jdx}] must be in [0, {modulus - 1}] for {direction_profile.name}"
            )
        directions.append(int(direction))

    spatial_frequency = _as_uint3(item.get("spatial_frequency", 4), field=f"strokes[{idx}].spatial_frequency")

    drift_speed = item.get("drift_speed", 1)
    if not isinstance(drift_speed, int) or not 0 <= int(drift_speed) <= 3:
        raise ChemosenseSchemaError(f"strokes[{idx}].drift_speed must be in [0, 3]")

    frame_index = item.get("frame_index")
    if frame_index is not None and (not isinstance(frame_index, int) or not 0 <= int(frame_index) <= 255):
        raise ChemosenseSchemaError(f"strokes[{idx}].frame_index must be in [0, 255]")

    delta_ms = item.get("delta_ms", 0)
    if not isinstance(delta_ms, int) or not 0 <= int(delta_ms) <= 255:
        raise ChemosenseSchemaError(f"strokes[{idx}].delta_ms must be in [0, 255]")

    commands: list[mental.MoveTo | mental.DrawDir] = [mental.MoveTo(start_x, start_y)]
    commands.extend(mental.DrawDir(direction, profile=direction_profile) for direction in directions)

    try:
        return mental.MentalStroke(
            commands=commands,
            form_class=form_class,
            symmetry=symmetry,
            direction_profile=direction_profile,
            spatial_frequency=spatial_frequency,
            drift_speed=int(drift_speed),
            frame_index=None if frame_index is None else int(frame_index),
            delta_ms=int(delta_ms),
        )
    except (TypeError, ValueError) as exc:
        raise ChemosenseSchemaError(f"invalid mental stroke at index {idx}: {exc}") from exc


def encode_smell_payload(payload: Mapping[str, Any] | dict[str, Any]) -> list[int]:
    """Encode smell payload using stable contract schema."""
    schema = _as_mapping(payload, kind="smell")
    strokes_raw = schema.get("strokes")
    if not isinstance(strokes_raw, Sequence) or not strokes_raw:
        raise ChemosenseSchemaError("smell payload requires non-empty `strokes`")

    strokes: list[smell.OdorStroke] = []
    for idx, item in enumerate(strokes_raw):
        if not isinstance(item, Mapping):
            raise ChemosenseSchemaError(f"strokes[{idx}] must be a mapping")
        strokes.append(_build_smell_stroke(item, idx))

    metadata = schema.get("metadata")
    if metadata is not None and not isinstance(metadata, Mapping):
        raise ChemosenseSchemaError("smell metadata must be a mapping when provided")

    if metadata is not None and "sniff_hz" in metadata:
        _as_uint3(int(metadata["sniff_hz"]), field="metadata.sniff_hz")

    try:
        return smell.encode_smell_strokes(strokes, metadata=dict(metadata) if metadata else None)
    except (TypeError, ValueError) as exc:
        raise ChemosenseSchemaError(f"invalid smell payload: {exc}") from exc


def decode_smell_payload(words: Iterable[int]) -> dict[str, Any]:
    packet_words = _as_words(words, field="smell words")
    try:
        metadata, strokes = smell.decode_smell_words(packet_words)
    except Exception as exc:
        raise ChemosensePacketError(f"failed to decode smell packet: {exc}") from exc

    if not strokes:
        raise ChemosensePacketError("smell packet decoded with no strokes")

    return {
        "metadata": metadata or {},
        "strokes": [
            {
                "category": stroke.category.name,
                "pleasantness_start": int(stroke.pleasantness_start),
                "intensity_start": int(stroke.intensity_start),
                "directions": [int(cmd.direction) for cmd in stroke.commands[1:] if isinstance(cmd, SmellDrawDir)],
            }
            for stroke in strokes
        ],
    }


def encode_taste_payload(payload: Mapping[str, Any] | dict[str, Any]) -> list[int]:
    """Encode taste payload using stable contract schema."""
    schema = _as_mapping(payload, kind="taste")
    events_raw = schema.get("events")
    if not isinstance(events_raw, Sequence) or not events_raw:
        raise ChemosenseSchemaError("taste payload requires non-empty `events`")

    events: list[taste.ZLayeredTasteEvent] = []
    for idx, item in enumerate(events_raw):
        if not isinstance(item, Mapping):
            raise ChemosenseSchemaError(f"events[{idx}] must be a mapping")
        events.append(_taste_event_payload_to_object(item, idx))

    adaptive = bool(schema.get("adaptive", False))
    try:
        return taste.pack_taste_zlayered(events, adaptive=adaptive)
    except (TypeError, ValueError) as exc:
        raise ChemosenseSchemaError(f"invalid taste payload: {exc}") from exc


def decode_taste_payload(words: Iterable[int]) -> dict[str, Any]:
    packet_words = _as_words(words, field="taste words")
    try:
        metadata, events = taste.unpack_taste_zlayered(packet_words)
    except Exception as exc:
        raise ChemosensePacketError(f"failed to decode taste packet: {exc}") from exc

    if not events:
        raise ChemosensePacketError("taste packet decoded with no events")

    return {
        "metadata": metadata or {},
        "events": [
            {
                "dominant_quality": event.dominant_quality.name,
                "secondary_quality": event.secondary_quality.name,
                "intensity": int(event.intensity),
                "intensity_direction": int(event.intensity_direction),
                "temporal_directions": [int(v) for v in event.temporal_directions],
                "duration": event.duration.name,
                "flavor_link": list(event.flavor_link) if event.flavor_link is not None else None,
            }
            for event in events
        ],
    }


def encode_touch_payload(payload: Mapping[str, Any] | dict[str, Any]) -> list[int]:
    """Encode touch payload using stable contract schema."""
    schema = _as_mapping(payload, kind="touch")
    strokes_raw = schema.get("strokes")
    if not isinstance(strokes_raw, Sequence) or not strokes_raw:
        raise ChemosenseSchemaError("touch payload requires non-empty `strokes`")

    strokes: list[touch.TouchStroke] = []
    for idx, item in enumerate(strokes_raw):
        if not isinstance(item, Mapping):
            raise ChemosenseSchemaError(f"strokes[{idx}] must be a mapping")
        strokes.append(_build_touch_stroke(item, idx))

    metadata = schema.get("metadata")
    if metadata is not None and not isinstance(metadata, Mapping):
        raise ChemosenseSchemaError("touch metadata must be a mapping when provided")

    try:
        return touch.pack_touch_strokes(strokes, metadata=dict(metadata) if metadata else None)
    except (TypeError, ValueError) as exc:
        raise ChemosenseSchemaError(f"invalid touch payload: {exc}") from exc


def decode_touch_payload(words: Iterable[int]) -> dict[str, Any]:
    packet_words = _as_words(words, field="touch words")
    try:
        metadata, strokes = touch.unpack_touch_words(packet_words)
    except Exception as exc:
        raise ChemosensePacketError(f"failed to decode touch packet: {exc}") from exc

    if not strokes:
        raise ChemosensePacketError("touch packet decoded with no strokes")

    return {
        "metadata": metadata or {},
        "strokes": [
            {
                "receptor": stroke.receptor.name,
                "region": stroke.region.name,
                "directions": [int(cmd.direction) for cmd in stroke.commands if isinstance(cmd, touch.DrawDir)],
                "pressure_profile": [int(v) for v in stroke.pressure_profile],
            }
            for stroke in strokes
        ],
    }


def encode_mental_payload(payload: Mapping[str, Any] | dict[str, Any]) -> list[int]:
    """Encode mental payload using stable contract schema."""
    schema = _as_mapping(payload, kind="mental")
    strokes_raw = schema.get("strokes")
    if not isinstance(strokes_raw, Sequence) or not strokes_raw:
        raise ChemosenseSchemaError("mental payload requires non-empty `strokes`")

    strokes: list[mental.MentalStroke] = []
    for idx, item in enumerate(strokes_raw):
        if not isinstance(item, Mapping):
            raise ChemosenseSchemaError(f"strokes[{idx}] must be a mapping")
        strokes.append(_build_mental_stroke(item, idx))

    metadata = schema.get("metadata")
    if metadata is not None and not isinstance(metadata, Mapping):
        raise ChemosenseSchemaError("mental metadata must be a mapping when provided")

    try:
        return mental.pack_mental_strokes(strokes, metadata=dict(metadata) if metadata else None)
    except (TypeError, ValueError) as exc:
        raise ChemosenseSchemaError(f"invalid mental payload: {exc}") from exc


def decode_mental_payload(words: Iterable[int]) -> dict[str, Any]:
    packet_words = _as_words(words, field="mental words")
    try:
        metadata, strokes = mental.unpack_mental_words(packet_words)
    except Exception as exc:
        raise ChemosensePacketError(f"failed to decode mental packet: {exc}") from exc

    if not strokes:
        raise ChemosensePacketError("mental packet decoded with no strokes")

    decoded_strokes: list[dict[str, Any]] = []
    for stroke in strokes:
        move = next((cmd for cmd in stroke.commands if isinstance(cmd, mental.MoveTo)), None)
        start = [0, 0] if move is None else [int(move.x), int(move.y)]
        directions = [int(cmd.direction) for cmd in stroke.commands if isinstance(cmd, mental.DrawDir)]
        decoded_strokes.append(
            {
                "form_class": stroke.form_class.name,
                "symmetry": stroke.symmetry.name,
                "direction_profile": stroke.direction_profile.name,
                "spatial_frequency": int(stroke.spatial_frequency),
                "drift_speed": int(stroke.drift_speed),
                "frame_index": stroke.frame_index,
                "delta_ms": int(stroke.delta_ms),
                "start": start,
                "directions": directions,
            }
        )

    return {
        "metadata": metadata or {},
        "strokes": decoded_strokes,
    }


def run_smoke_flow() -> dict[str, Any]:
    """Execute deterministic end-to-end chemosense smoke flow used by API + CLI."""
    smell_payload = {
        "metadata": {"sniff_hz": 2},
        "strokes": [
            {
                "category": "FLORAL",
                "pleasantness_start": 4,
                "intensity_start": 1,
                "directions": [0, 1, 2, 3],
            },
            {
                "category": "WOODY_EARTHY",
                "pleasantness_start": 3,
                "intensity_start": 2,
                "directions": [4, 5, 6, 7],
            },
        ],
    }

    taste_payload = {
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

    touch_payload = {
        "strokes": [
            {
                "receptor": "SA_I",
                "region": "INDEX_TIP",
                "directions": [0, 2, 4],
                "pressure_profile": [3, 4, 3],
            },
            {
                "receptor": "RA_II",
                "region": "PALM_CENTER",
                "directions": [6, 6, 2],
                "pressure_profile": [1, 3, 5],
            },
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
                "frame_index": 0,
                "delta_ms": 17,
                "start": [128, 128],
                "directions": [0, 1, 2, 3, 4, 5, 6, 7],
            },
            {
                "form_class": "LATTICE",
                "symmetry": "D6",
                "direction_profile": "D6_12",
                "spatial_frequency": 3,
                "drift_speed": 2,
                "frame_index": 1,
                "delta_ms": 33,
                "start": [96, 96],
                "directions": [0, 2, 4, 6, 8, 10],
            },
        ]
    }

    smell_words = encode_smell_payload(smell_payload)
    smell_decoded = decode_smell_payload(smell_words)

    taste_words = encode_taste_payload(taste_payload)
    taste_decoded = decode_taste_payload(taste_words)

    touch_words = encode_touch_payload(touch_payload)
    touch_decoded = decode_touch_payload(touch_words)

    mental_words = encode_mental_payload(mental_payload)
    mental_decoded = decode_mental_payload(mental_words)

    taste_events = [_taste_event_payload_to_object(event, idx) for idx, event in enumerate(taste_payload["events"])]
    smell_packets = [encode_smell_payload({"strokes": [stroke]}) for stroke in smell_payload["strokes"]]
    touch_packets = [
        encode_touch_payload({"strokes": [touch_payload["strokes"][idx]]})
        for idx in range(min(len(taste_events), len(touch_payload["strokes"])))
    ]

    fused_words = taste.pack_fused_multimodal(
        taste_events=taste_events,
        smell_packets=smell_packets,
        touch_packets=touch_packets,
        adaptive=True,
    )
    scheduler = taste.FusionScheduler()
    ingest = scheduler.ingest_stream(fused_words)
    fused_events = scheduler.fuse_zlayer_events()

    return {
        "command": "chemosense-smoke",
        "smell_word_count": int(len(smell_words)),
        "smell_stroke_count": int(len(smell_decoded["strokes"])),
        "smell_meta": smell_decoded["metadata"],
        "taste_word_count": int(len(taste_words)),
        "taste_event_count": int(len(taste_decoded["events"])),
        "taste_meta": taste_decoded["metadata"],
        "touch_word_count": int(len(touch_words)),
        "touch_stroke_count": int(len(touch_decoded["strokes"])),
        "touch_meta": touch_decoded["metadata"],
        "mental_word_count": int(len(mental_words)),
        "mental_stroke_count": int(len(mental_decoded["strokes"])),
        "mental_meta": mental_decoded["metadata"],
        "fused_word_count": int(len(fused_words)),
        "fused_event_count": int(len(fused_events)),
        "ingest": ingest,
        "touch_placeholder_removed": True,
        "exit_code": 0,
    }
