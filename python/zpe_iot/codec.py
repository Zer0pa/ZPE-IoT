from __future__ import annotations

import os
import zlib
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Sequence, Tuple, Union

import numpy as np

from .presets import preset_config

LOG_BASE = 1.091928
LOG_MAG_TABLE = np.array([round(LOG_BASE**i) for i in range(64)], dtype=np.int32)

ADAPTIVE_K = 0.15
ADAPTIVE_THR_MIN = 0.001
ADAPTIVE_THR_MAX = 1.0
ADAPTIVE_ALPHA = 0.95

PACKET_MAGIC = 0x5A50
PACKET_MAGIC_ZERO_SPECIAL = 0x5A51
PACKET_VERSION = 0x01
PACKET_FLAG_COMPACT_RUNS = 0x01
CRC_POLY = 0x1021
WI1_MAGIC = b"ZW1"
WI1_VERSION = 1
ZH1_MAGIC = b"ZH1"
ZH1_VERSION = 1

DIRECTION_DELTAS = {
    0: 0.0,
    1: 1.0,
    2: 2.0,
    3: 4.0,
    4: 8.0,
    5: -8.0,
    6: -2.0,
    7: -1.0,
}


class Mode(str, Enum):
    FAST = "fast"
    BALANCED = "balanced"
    LOSSLESS_DELTA = "lossless_delta"


@dataclass
class Config:
    mode: Mode = Mode.BALANCED
    threshold: float = 0.05
    step: float = 0.0
    bands: Tuple[float, float, float] = (1.0, 4.0, 16.0)
    adaptive: bool = True
    thr_min: float = ADAPTIVE_THR_MIN
    thr_max: float = ADAPTIVE_THR_MAX
    alpha: float = ADAPTIVE_ALPHA
    k: float = ADAPTIVE_K
    preset_id: int = 8

    @classmethod
    def from_preset(cls, preset: str) -> "Config":
        cfg = preset_config(preset)
        return cls(
            mode=Mode(cfg["mode"]),
            threshold=float(cfg["threshold"]),
            step=float(cfg["step"]),
            bands=tuple(float(v) for v in cfg["bands"]),
            adaptive=True,
            thr_min=ADAPTIVE_THR_MIN,
            thr_max=ADAPTIVE_THR_MAX,
            alpha=ADAPTIVE_ALPHA,
            k=ADAPTIVE_K,
            preset_id=int(cfg["preset_id"]),
        )


@dataclass
class EncodedStream:
    rle_tokens: List[Tuple[int, int, int]]
    start_value: float
    step: float
    mode: Mode
    sample_count: int
    adaptive: bool = True
    preset_id: int = 8

    def to_bytes(self, compact: bool | None = None) -> bytes:
        return pack_stream(self, compact=compact)

    @classmethod
    def from_bytes(cls, packet: bytes) -> "EncodedStream":
        return unpack_stream(packet)

    @property
    def packed_size(self) -> int:
        return len(self.to_bytes())

    @property
    def compression_ratio(self) -> float:
        if self.sample_count <= 0:
            return 0.0
        return (self.sample_count * 8.0) / max(1, self.packed_size)

    def nrmse(self, original: Sequence[float]) -> float:
        return compute_nrmse(np.asarray(original, dtype=np.float64), decode(self))


class EncodeError(Exception):
    pass


def _direction_sign(direction: int) -> float:
    if 1 <= direction <= 4:
        return 1.0
    if 5 <= direction <= 7:
        return -1.0
    return 0.0


def _quantise_delta(delta: float, threshold: float, bands: Tuple[float, float, float]) -> int:
    abs_delta = abs(delta)
    if abs_delta < threshold:
        return 0

    # Presets store [1,4,16]-style factors; expand to boundaries [4x,16x,64x].
    gentle = max(bands[0], 1.0) * 4.0
    moderate = max(bands[1], gentle) * 4.0
    steep = max(bands[2], bands[1], gentle) * 4.0

    if delta > 0:
        if abs_delta < gentle * threshold:
            return 1
        if abs_delta < moderate * threshold:
            return 2
        if abs_delta < steep * threshold:
            return 3
        return 4

    if abs_delta < gentle * threshold:
        return 7
    if abs_delta < steep * threshold:
        return 6
    return 5


def _find_magnitude(abs_delta: float, step: float) -> int:
    if abs_delta <= 0.0 or step <= 0.0:
        return 0
    target = abs_delta / step
    return int(np.argmin(np.abs(LOG_MAG_TABLE - target)))


def _auto_step(samples: np.ndarray) -> float:
    std = float(np.std(samples))
    if std <= 0.0:
        return 0.001
    return std / 64.0


def _coerce_mode(mode: Union[str, Mode]) -> Mode:
    return mode if isinstance(mode, Mode) else Mode(str(mode).lower())


def _resolve_config(
    config: Config | None,
    preset: str | None,
    kwargs: dict,
) -> Config:
    if config is not None and preset is not None:
        raise ValueError("Provide either config or preset, not both")

    if config is None:
        config = Config.from_preset(preset) if preset else Config()

    if kwargs:
        updates = dict(kwargs)
        if "mode" in updates:
            updates["mode"] = _coerce_mode(updates["mode"])
        if "bands" in updates:
            bands = tuple(float(v) for v in updates["bands"])
            if len(bands) != 3:
                raise ValueError("bands must contain exactly 3 values")
            updates["bands"] = bands
        config = Config(**{**config.__dict__, **updates})
    return config


def encode(
    samples: Sequence[float] | np.ndarray,
    config: Config | None = None,
    preset: str | None = None,
    **kwargs,
) -> EncodedStream:
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim != 1:
        raise EncodeError("samples must be a 1D sequence")
    if len(x) == 0:
        raise EncodeError("samples must not be empty")

    cfg = _resolve_config(config, preset, kwargs)
    mode = _coerce_mode(cfg.mode)
    step = float(cfg.step) if float(cfg.step) > 0.0 else _auto_step(x)
    threshold = float(cfg.threshold) if float(cfg.threshold) > 0.0 else float(cfg.thr_min)

    if len(x) == 1:
        return EncodedStream([], float(x[0]), step, mode, 1, cfg.adaptive, cfg.preset_id)

    reconstructed = float(x[0])
    envelope = threshold / max(cfg.k, 1e-9)

    rle_tokens: List[Tuple[int, int, int]] = []
    curr_d = 0
    curr_m = 0
    curr_count = 0

    for sample in x[1:]:
        delta = float(sample - reconstructed)

        if cfg.adaptive:
            envelope = max(cfg.alpha * envelope, abs(delta))
            threshold = float(np.clip(cfg.k * envelope, cfg.thr_min, cfg.thr_max))

        d = _quantise_delta(delta, threshold, cfg.bands)

        if mode == Mode.FAST:
            m_idx = 0
            reconstructed_delta = DIRECTION_DELTAS[d] * step
        else:
            if d == 0:
                m_idx = 0
                reconstructed_delta = 0.0
            else:
                m_idx = _find_magnitude(abs(delta), step)
                reconstructed_delta = _direction_sign(d) * float(LOG_MAG_TABLE[m_idx]) * step

        if curr_count > 0 and d == curr_d and m_idx == curr_m and curr_count < 65535:
            curr_count += 1
        else:
            if curr_count > 0:
                rle_tokens.append((curr_d, curr_m, curr_count))
            curr_d = d
            curr_m = m_idx
            curr_count = 1

        reconstructed += reconstructed_delta

    if curr_count > 0:
        rle_tokens.append((curr_d, curr_m, curr_count))

    return EncodedStream(
        rle_tokens=rle_tokens,
        start_value=float(x[0]),
        step=step,
        mode=mode,
        sample_count=len(x),
        adaptive=cfg.adaptive,
        preset_id=cfg.preset_id,
    )


def decode(stream: EncodedStream | bytes | bytearray) -> np.ndarray:
    if isinstance(stream, (bytes, bytearray)):
        stream = unpack_stream(bytes(stream))

    out = np.zeros(stream.sample_count, dtype=np.float64)
    if stream.sample_count == 0:
        return out

    out[0] = stream.start_value
    idx = 1
    value = stream.start_value

    for d, m_idx, count in stream.rle_tokens:
        if stream.mode == Mode.FAST:
            delta = DIRECTION_DELTAS[d] * stream.step
        else:
            if d == 0:
                delta = 0.0
            else:
                delta = _direction_sign(d) * float(LOG_MAG_TABLE[m_idx]) * stream.step

        for _ in range(int(count)):
            if idx >= stream.sample_count:
                break
            value += delta
            out[idx] = value
            idx += 1
    return out


def compute_nrmse(original: np.ndarray, reconstructed: np.ndarray) -> float:
    n = min(len(original), len(reconstructed))
    if n == 0:
        return 0.0
    x = original[:n].astype(np.float64)
    y = reconstructed[:n].astype(np.float64)
    mse = float(np.mean((x - y) ** 2))
    dynamic_range = float(np.max(x) - np.min(x))
    if dynamic_range <= 1e-12:
        return 0.0 if mse <= 1e-12 else 1.0
    return float(np.sqrt(mse) / dynamic_range)


def compute_cr(stream: EncodedStream, original_samples: Sequence[float] | np.ndarray) -> float:
    raw_bytes = np.asarray(original_samples, dtype=np.float64).nbytes
    return raw_bytes / max(1, stream.packed_size)


def _crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ CRC_POLY) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def _step_to_fixed(step: float) -> int:
    val = int(round(step * 10000.0))
    return int(np.clip(val, 1, 65535))


def _fixed_to_step(step_fixed: int) -> float:
    return float(step_fixed) / 10000.0


def _wi1_enabled() -> bool:
    return os.getenv("ZPE_IOT_WI1_ENTROPY_STAGE", "0") == "1"


def _zh1_enabled() -> bool:
    return os.getenv("ZPE_IOT_ZH1_DERIVATIVE_STAGE", "0") == "1"


def _delta_encode_bytes(payload: bytes) -> bytes:
    if not payload:
        return payload
    out = bytearray(len(payload))
    prev = payload[0]
    out[0] = prev
    for i in range(1, len(payload)):
        cur = payload[i]
        out[i] = (cur - prev) & 0xFF
        prev = cur
    return bytes(out)


def _delta_decode_bytes(payload: bytes) -> bytes:
    if not payload:
        return payload
    out = bytearray(len(payload))
    acc = payload[0]
    out[0] = acc
    for i in range(1, len(payload)):
        acc = (acc + payload[i]) & 0xFF
        out[i] = acc
    return bytes(out)


def _maybe_wrap_wi1(packet: bytes) -> bytes:
    if not _wi1_enabled():
        return packet

    # WI-1 (experimental): entropy-stage wrapper over the deterministic packet stream.
    compressed = zlib.compress(packet, level=1)
    wrapped = WI1_MAGIC + bytes([WI1_VERSION]) + len(packet).to_bytes(4, "little") + compressed
    return wrapped if len(wrapped) < len(packet) else packet


def _maybe_unwrap_wi1(packet: bytes) -> bytes:
    if len(packet) < 8 or packet[:3] != WI1_MAGIC:
        return packet

    if packet[3] != WI1_VERSION:
        raise ValueError("Unsupported WI-1 packet version")

    expected_len = int.from_bytes(packet[4:8], "little")
    inner = zlib.decompress(packet[8:])
    if expected_len > 0 and len(inner) != expected_len:
        raise ValueError("WI-1 payload length mismatch")
    return inner


def _maybe_wrap_zh1(packet: bytes) -> bytes:
    if not _zh1_enabled():
        return packet
    shaped = _delta_encode_bytes(packet)
    compressed = zlib.compress(shaped, level=1)
    wrapped = ZH1_MAGIC + bytes([ZH1_VERSION]) + len(packet).to_bytes(4, "little") + compressed
    return wrapped if len(wrapped) < len(packet) else packet


def _maybe_unwrap_zh1(packet: bytes) -> bytes:
    if len(packet) < 8 or packet[:3] != ZH1_MAGIC:
        return packet
    if packet[3] != ZH1_VERSION:
        raise ValueError("Unsupported ZH-1 packet version")
    expected_len = int.from_bytes(packet[4:8], "little")
    shaped = zlib.decompress(packet[8:])
    inner = _delta_decode_bytes(shaped)
    if expected_len > 0 and len(inner) != expected_len:
        raise ValueError("ZH-1 payload length mismatch")
    return inner


def _iter_balanced_chunks(rle_tokens: Sequence[Tuple[int, int, int]]) -> Iterable[Tuple[int, int, int]]:
    for d, m, count in rle_tokens:
        remaining = int(count)
        while remaining > 0:
            chunk = min(remaining, 127)
            yield int(d), int(m), chunk
            remaining -= chunk


def _append_bits(payload: bytearray, scratch: int, scratch_bits: int, value: int, width: int) -> tuple[int, int]:
    scratch = (scratch << width) | (int(value) & ((1 << width) - 1))
    scratch_bits += width

    while scratch_bits >= 8:
        scratch_bits -= 8
        payload.append((scratch >> scratch_bits) & 0xFF)
        scratch &= (1 << scratch_bits) - 1 if scratch_bits else 0

    return scratch, scratch_bits


def _flush_bits(payload: bytearray, scratch: int, scratch_bits: int) -> None:
    if scratch_bits:
        payload.append((scratch << (8 - scratch_bits)) & 0xFF)


def _read_bits(payload: bytes, bit_pos: int, width: int) -> tuple[int, int]:
    total_bits = len(payload) * 8
    if bit_pos + width > total_bits:
        raise ValueError("Corrupt compact payload length")

    value = 0
    for _ in range(width):
        byte = payload[bit_pos >> 3]
        shift = 7 - (bit_pos & 7)
        value = (value << 1) | ((byte >> shift) & 0x01)
        bit_pos += 1
    return value, bit_pos


def _padding_is_zero(payload: bytes, bit_pos: int) -> bool:
    total_bits = len(payload) * 8
    while bit_pos < total_bits:
        byte = payload[bit_pos >> 3]
        shift = 7 - (bit_pos & 7)
        if ((byte >> shift) & 0x01) != 0:
            return False
        bit_pos += 1
    return True


def _pack_balanced_payload(rle_tokens: Sequence[Tuple[int, int, int]], compact: bool) -> bytes:
    payload = bytearray()

    if not compact:
        for d, m, chunk in _iter_balanced_chunks(rle_tokens):
            token = ((d & 0x07) << 13) | ((m & 0x3F) << 7) | (chunk & 0x7F)
            payload += int(token).to_bytes(2, "big")
        return bytes(payload)

    scratch = 0
    scratch_bits = 0
    for d, m, chunk in _iter_balanced_chunks(rle_tokens):
        if chunk == 1:
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, 0, 1)
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, d, 3)
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, m, 6)
        else:
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, 1, 1)
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, d, 3)
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, m, 6)
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, chunk, 7)

    _flush_bits(payload, scratch, scratch_bits)
    return bytes(payload)


def _pack_zero_special_payload(rle_tokens: Sequence[Tuple[int, int, int]]) -> bytes:
    payload = bytearray()
    scratch = 0
    scratch_bits = 0

    for d, m, chunk in _iter_balanced_chunks(rle_tokens):
        if d == 0 and m == 0:
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, 0, 1)
            if chunk == 1:
                scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, 0, 1)
            else:
                scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, 1, 1)
                scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, chunk - 2, 7)
            continue

        scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, 1, 1)
        if chunk == 1:
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, 0, 1)
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, d, 3)
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, m, 6)
        else:
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, 1, 1)
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, d, 3)
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, m, 6)
            scratch, scratch_bits = _append_bits(payload, scratch, scratch_bits, chunk, 7)

    _flush_bits(payload, scratch, scratch_bits)
    return bytes(payload)


def _unpack_balanced_payload(payload: bytes, sample_count: int, compact: bool) -> List[Tuple[int, int, int]]:
    rle_tokens: List[Tuple[int, int, int]] = []

    if not compact:
        if len(payload) % 2 != 0:
            raise ValueError("Corrupt payload length")
        for i in range(0, len(payload), 2):
            token = int.from_bytes(payload[i : i + 2], "big")
            d = (token >> 13) & 0x07
            m = (token >> 7) & 0x3F
            count = token & 0x7F
            if count > 0:
                rle_tokens.append((d, m, count))
        return rle_tokens

    bit_pos = 0
    emitted = 0
    target = max(0, sample_count - 1)

    while emitted < target:
        prefix, bit_pos = _read_bits(payload, bit_pos, 1)
        d, bit_pos = _read_bits(payload, bit_pos, 3)
        m, bit_pos = _read_bits(payload, bit_pos, 6)
        if prefix == 0:
            count = 1
        else:
            count, bit_pos = _read_bits(payload, bit_pos, 7)
            if count == 0:
                raise ValueError("Corrupt compact payload count")
        emitted += count
        if emitted > target:
            raise ValueError("Corrupt compact payload count")
        rle_tokens.append((d, m, count))

    if not _padding_is_zero(payload, bit_pos):
        raise ValueError("Corrupt compact payload padding")

    return rle_tokens


def _unpack_zero_special_payload(payload: bytes, sample_count: int) -> List[Tuple[int, int, int]]:
    rle_tokens: List[Tuple[int, int, int]] = []
    bit_pos = 0
    emitted = 0
    target = max(0, sample_count - 1)

    while emitted < target:
        family, bit_pos = _read_bits(payload, bit_pos, 1)
        subtype, bit_pos = _read_bits(payload, bit_pos, 1)

        if family == 0:
            if subtype == 0:
                count = 1
            else:
                encoded_count, bit_pos = _read_bits(payload, bit_pos, 7)
                count = encoded_count + 2
            d = 0
            m = 0
        elif subtype == 0:
            d, bit_pos = _read_bits(payload, bit_pos, 3)
            m, bit_pos = _read_bits(payload, bit_pos, 6)
            count = 1
        else:
            d, bit_pos = _read_bits(payload, bit_pos, 3)
            m, bit_pos = _read_bits(payload, bit_pos, 6)
            count, bit_pos = _read_bits(payload, bit_pos, 7)
            if count == 0:
                raise ValueError("Corrupt zero-special payload count")

        emitted += count
        if emitted > target:
            raise ValueError("Corrupt zero-special payload count")
        rle_tokens.append((d, m, count))

    if not _padding_is_zero(payload, bit_pos):
        raise ValueError("Corrupt zero-special payload padding")

    return rle_tokens


def pack_stream(
    stream: EncodedStream,
    compact: bool | None = None,
    zero_special: bool | None = None,
) -> bytes:
    header = bytearray()
    magic = PACKET_MAGIC

    mode_bits = {Mode.FAST: 0, Mode.BALANCED: 1, Mode.LOSSLESS_DELTA: 2}[stream.mode]
    use_compact = bool(stream.mode != Mode.FAST) if compact is None else bool(compact and stream.mode != Mode.FAST)
    flags = (mode_bits << 6) | ((int(stream.preset_id) & 0x0F) << 2) | ((1 if stream.adaptive else 0) << 1)
    if use_compact:
        flags |= PACKET_FLAG_COMPACT_RUNS

    payload = bytearray()
    if stream.mode == Mode.FAST:
        for d, _m, count in stream.rle_tokens:
            remaining = int(count)
            while remaining > 0:
                chunk = min(remaining, 31)
                payload.append(((int(d) & 0x07) << 5) | (chunk & 0x1F))
                remaining -= chunk
    else:
        if use_compact:
            compact_payload = _pack_balanced_payload(stream.rle_tokens, compact=True)
            if zero_special is False:
                payload += compact_payload
            else:
                zero_special_payload = _pack_zero_special_payload(stream.rle_tokens)
                use_zero_special = zero_special is True or len(zero_special_payload) < len(compact_payload)
                payload += zero_special_payload if use_zero_special else compact_payload
                if use_zero_special:
                    magic = PACKET_MAGIC_ZERO_SPECIAL
        else:
            payload += _pack_balanced_payload(stream.rle_tokens, compact=False)

    header += int(magic).to_bytes(2, "little")
    header += bytes([PACKET_VERSION])
    header += bytes([flags])
    header += int(stream.sample_count).to_bytes(2, "little")
    header += np.float32(stream.start_value).tobytes()
    header += int(_step_to_fixed(stream.step)).to_bytes(2, "little")

    packet = bytes(header + payload)
    crc = _crc16_ccitt(packet)
    return _maybe_wrap_zh1(_maybe_wrap_wi1(packet + int(crc).to_bytes(2, "little")))


def unpack_stream(packet: bytes) -> EncodedStream:
    packet = _maybe_unwrap_wi1(_maybe_unwrap_zh1(packet))
    if len(packet) < 14:
        raise ValueError("Packet too short")

    magic = int.from_bytes(packet[0:2], "little")
    if magic not in {PACKET_MAGIC, PACKET_MAGIC_ZERO_SPECIAL}:
        raise ValueError("Bad packet magic")
    if packet[2] != PACKET_VERSION:
        raise ValueError("Unsupported packet version")

    expected_crc = int.from_bytes(packet[-2:], "little")
    actual_crc = _crc16_ccitt(packet[:-2])
    if expected_crc != actual_crc:
        raise ValueError("CRC mismatch")

    flags = packet[3]
    mode_bits = (flags >> 6) & 0x03
    mode = {0: Mode.FAST, 1: Mode.BALANCED, 2: Mode.LOSSLESS_DELTA}.get(mode_bits)
    if mode is None:
        raise ValueError("Invalid mode")

    preset_id = (flags >> 2) & 0x0F
    adaptive = ((flags >> 1) & 0x01) == 1
    compact = (flags & PACKET_FLAG_COMPACT_RUNS) == PACKET_FLAG_COMPACT_RUNS

    sample_count = int.from_bytes(packet[4:6], "little")
    start_value = float(np.frombuffer(packet[6:10], dtype=np.float32)[0])
    step = _fixed_to_step(int.from_bytes(packet[10:12], "little"))

    payload = packet[12:-2]

    if mode == Mode.FAST:
        rle_tokens: List[Tuple[int, int, int]] = []
        for b in payload:
            d = (b >> 5) & 0x07
            count = b & 0x1F
            if count > 0:
                rle_tokens.append((d, 0, count))
    else:
        if magic == PACKET_MAGIC_ZERO_SPECIAL and compact:
            rle_tokens = _unpack_zero_special_payload(payload, sample_count=sample_count)
        else:
            rle_tokens = _unpack_balanced_payload(payload, sample_count=sample_count, compact=compact)

    return EncodedStream(
        rle_tokens=rle_tokens,
        start_value=start_value,
        step=step,
        mode=mode,
        sample_count=sample_count,
        adaptive=adaptive,
        preset_id=preset_id,
    )
