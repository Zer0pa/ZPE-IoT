from __future__ import annotations

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
PACKET_VERSION = 0x01
CRC_POLY = 0x1021

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

    def to_bytes(self) -> bytes:
        return pack_stream(self)

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


def pack_stream(stream: EncodedStream) -> bytes:
    header = bytearray()
    header += int(PACKET_MAGIC).to_bytes(2, "little")
    header += bytes([PACKET_VERSION])

    mode_bits = {Mode.FAST: 0, Mode.BALANCED: 1, Mode.LOSSLESS_DELTA: 2}[stream.mode]
    flags = (mode_bits << 6) | ((int(stream.preset_id) & 0x0F) << 2) | ((1 if stream.adaptive else 0) << 1)
    header += bytes([flags])

    header += int(stream.sample_count).to_bytes(2, "little")
    header += np.float32(stream.start_value).tobytes()
    header += int(_step_to_fixed(stream.step)).to_bytes(2, "little")

    payload = bytearray()
    if stream.mode == Mode.FAST:
        for d, _m, count in stream.rle_tokens:
            remaining = int(count)
            while remaining > 0:
                chunk = min(remaining, 31)
                payload.append(((int(d) & 0x07) << 5) | (chunk & 0x1F))
                remaining -= chunk
    else:
        for d, m, count in stream.rle_tokens:
            remaining = int(count)
            while remaining > 0:
                chunk = min(remaining, 127)
                token = ((int(d) & 0x07) << 13) | ((int(m) & 0x3F) << 7) | (chunk & 0x7F)
                payload += int(token).to_bytes(2, "big")
                remaining -= chunk

    packet = bytes(header + payload)
    crc = _crc16_ccitt(packet)
    return packet + int(crc).to_bytes(2, "little")


def unpack_stream(packet: bytes) -> EncodedStream:
    if len(packet) < 14:
        raise ValueError("Packet too short")

    if int.from_bytes(packet[0:2], "little") != PACKET_MAGIC:
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

    sample_count = int.from_bytes(packet[4:6], "little")
    start_value = float(np.frombuffer(packet[6:10], dtype=np.float32)[0])
    step = _fixed_to_step(int.from_bytes(packet[10:12], "little"))

    payload = packet[12:-2]
    rle_tokens: List[Tuple[int, int, int]] = []

    if mode == Mode.FAST:
        for b in payload:
            d = (b >> 5) & 0x07
            count = b & 0x1F
            if count > 0:
                rle_tokens.append((d, 0, count))
    else:
        if len(payload) % 2 != 0:
            raise ValueError("Corrupt payload length")
        for i in range(0, len(payload), 2):
            token = int.from_bytes(payload[i : i + 2], "big")
            d = (token >> 13) & 0x07
            m = (token >> 7) & 0x3F
            count = token & 0x7F
            if count > 0:
                rle_tokens.append((d, m, count))

    return EncodedStream(
        rle_tokens=rle_tokens,
        start_value=start_value,
        step=step,
        mode=mode,
        sample_count=sample_count,
        adaptive=adaptive,
        preset_id=preset_id,
    )
