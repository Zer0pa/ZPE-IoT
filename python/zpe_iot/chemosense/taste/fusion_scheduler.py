from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .pack import unpack_taste_zlayered, unpack_taste_zlevel_word
from .types import TasteZLevel, ZLayeredTasteEvent

TASTE_TYPE_BIT = 0x0400
SMELL_TYPE_BIT = 0x0200
TOUCH_TYPE_BIT = 0x0800

MODE_EXTENSION = 0b10
DEFAULT_VERSION = 0
TOUCH_HEADER_VERSION = 1
TOUCH_DATA_VERSION = 0
TOUCH_HEADER_TAG = 0x001F


@dataclass(frozen=True)
class FlavorEvent:
    index: int
    taste_words: tuple[int, ...]
    smell_words: tuple[int, ...]
    touch_words: tuple[int, ...]
    taste_event: ZLayeredTasteEvent

    def signature(self) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
        return (self.taste_words, self.smell_words, self.touch_words)


class FusionScheduler:
    """Deterministic multimodal fusion scheduler for taste+smell+touch streams."""

    def __init__(self) -> None:
        self._raw_stream: list[int] = []
        self._taste_packets: list[list[int]] = []
        self._smell_packets: list[list[int]] = []
        self._touch_packets: list[list[int]] = []
        self._fused_events: list[FlavorEvent] = []

    def ingest_stream(self, words: Iterable[int]) -> dict[str, int]:
        new_words = [int(word) for word in words]
        self._raw_stream.extend(new_words)

        self._taste_packets, self._smell_packets, self._touch_packets = _extract_all_packets(self._raw_stream)

        return {
            "total_words": len(self._raw_stream),
            "taste_packets": len(self._taste_packets),
            "smell_packets": len(self._smell_packets),
            "touch_packets": len(self._touch_packets),
        }

    def fuse_zlayer_events(self) -> list[FlavorEvent]:
        fused: list[FlavorEvent] = []
        boundary = min(len(self._taste_packets), len(self._smell_packets), len(self._touch_packets))

        for index in range(boundary):
            taste_words = self._taste_packets[index]
            _meta, decoded_taste = unpack_taste_zlayered(taste_words)
            if not decoded_taste:
                continue

            fused.append(
                FlavorEvent(
                    index=index,
                    taste_words=tuple(taste_words),
                    smell_words=tuple(self._smell_packets[index]),
                    touch_words=tuple(self._touch_packets[index]),
                    taste_event=decoded_taste[0],
                )
            )

        self._fused_events = fused
        return list(fused)

    def emit_fused_words(self) -> list[int]:
        emitted: list[int] = []
        for event in self._fused_events:
            emitted.extend(event.taste_words)
            emitted.extend(event.smell_words)
            emitted.extend(event.touch_words)
        return emitted

    @property
    def fused_events(self) -> list[FlavorEvent]:
        return list(self._fused_events)



def _word_mode(word: int) -> int:
    return (word >> 18) & 0x3


def _word_version(word: int) -> int:
    return (word >> 16) & 0x3


def _word_payload(word: int) -> int:
    return word & 0xFFFF


def _is_extension(word: int) -> bool:
    return _word_mode(word) == MODE_EXTENSION


def _is_smell_word(word: int) -> bool:
    return _is_extension(word) and (word & SMELL_TYPE_BIT) != 0


def _is_touch_word(word: int) -> bool:
    return _is_extension(word) and (word & TOUCH_TYPE_BIT) != 0


def _is_touch_header(word: int) -> bool:
    return _is_touch_word(word) and _word_version(word) == TOUCH_HEADER_VERSION and (word & TOUCH_HEADER_TAG) == TOUCH_HEADER_TAG


def _consume_taste_packet(words: list[int], index: int) -> tuple[list[int], int] | None:
    first = unpack_taste_zlevel_word(words[index])
    if first is None or first[0] != TasteZLevel.QUALITY:
        return None
    if index + 3 >= len(words):
        return None

    second = unpack_taste_zlevel_word(words[index + 1])
    t0 = unpack_taste_zlevel_word(words[index + 2])
    t1 = unpack_taste_zlevel_word(words[index + 3])
    if (
        second is None
        or second[0] != TasteZLevel.INTENSITY
        or t0 is None
        or t0[0] != TasteZLevel.TEMPORAL
        or t1 is None
        or t1[0] != TasteZLevel.TEMPORAL
    ):
        return None

    use_coarse = (second[1] & 0x80) != 0
    consumed = 4
    if not use_coarse:
        if index + 4 >= len(words):
            return None
        t2 = unpack_taste_zlevel_word(words[index + 4])
        if t2 is None or t2[0] != TasteZLevel.TEMPORAL:
            return None
        consumed = 5

    maybe_flavor_index = index + consumed
    if maybe_flavor_index < len(words):
        maybe_flavor = unpack_taste_zlevel_word(words[maybe_flavor_index])
        if maybe_flavor is not None and maybe_flavor[0] == TasteZLevel.FLAVOR:
            consumed += 1
    return words[index : index + consumed], consumed


def _consume_smell_packet(words: list[int], index: int) -> tuple[list[int], int] | None:
    word = words[index]
    if not _is_smell_word(word) or _word_version(word) != DEFAULT_VERSION:
        return None
    payload = _word_payload(word)
    if ((payload >> 6) & 0x3) != 0:  # smell header A
        return None
    if index + 1 >= len(words):
        return None

    second_word = words[index + 1]
    if not _is_smell_word(second_word) or _word_version(second_word) != DEFAULT_VERSION:
        return None
    payload_b = _word_payload(second_word)
    if ((payload_b >> 6) & 0x3) != 1:  # smell header B
        return None

    step_count = payload_b & 0x7
    consumed = 2
    cursor = index + 2
    while consumed < 2 + step_count and cursor < len(words):
        step_word = words[cursor]
        if not _is_smell_word(step_word) or _word_version(step_word) != DEFAULT_VERSION:
            break
        if ((_word_payload(step_word) >> 6) & 0x3) != 2:
            break
        consumed += 1
        cursor += 1

    # Preserve trailing smell metadata words (OP_META) when present.
    while cursor < len(words):
        meta_word = words[cursor]
        if not _is_smell_word(meta_word) or _word_version(meta_word) != DEFAULT_VERSION:
            break
        if ((_word_payload(meta_word) >> 6) & 0x3) != 3:
            break
        consumed += 1
        cursor += 1
    return words[index : index + consumed], consumed


def _consume_touch_packet(words: list[int], index: int) -> tuple[list[int], int] | None:
    header = words[index]
    if not _is_touch_header(header):
        return None
    cursor = index + 1
    while cursor < len(words):
        word = words[cursor]
        if not _is_touch_word(word):
            break
        if _is_touch_header(word):
            break
        if _word_version(word) != TOUCH_DATA_VERSION:
            break
        cursor += 1
    return words[index:cursor], cursor - index


def _extract_all_packets(words: list[int]) -> tuple[list[list[int]], list[list[int]], list[list[int]]]:
    taste_packets: list[list[int]] = []
    smell_packets: list[list[int]] = []
    touch_packets: list[list[int]] = []

    index = 0
    while index < len(words):
        consumed: tuple[list[int], int] | None

        consumed = _consume_taste_packet(words, index)
        if consumed is not None:
            packet, size = consumed
            taste_packets.append(packet)
            index += size
            continue

        consumed = _consume_smell_packet(words, index)
        if consumed is not None:
            packet, size = consumed
            smell_packets.append(packet)
            index += size
            continue

        consumed = _consume_touch_packet(words, index)
        if consumed is not None:
            packet, size = consumed
            touch_packets.append(packet)
            index += size
            continue

        index += 1

    return taste_packets, smell_packets, touch_packets
