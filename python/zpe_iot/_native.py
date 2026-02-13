from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import numpy as np
from cffi import FFI

from .codec import Config, Mode

_FFI = FFI()
_FFI.cdef(
    """
    typedef struct {
        uint8_t mode;
        double threshold;
        double step;
        double bands0;
        double bands1;
        double bands2;
        uint8_t adaptive;
        double thr_min;
        double thr_max;
        double alpha;
        double k;
        uint8_t preset_id;
    } zpe_iot_config_t;

    int32_t zpe_iot_encode(const double* samples, size_t n_samples,
                           const zpe_iot_config_t* config,
                           uint8_t* out_bytes, size_t out_capacity);

    int32_t zpe_iot_decode(const uint8_t* packed, size_t packed_len,
                           double* out_samples, size_t out_capacity);
    """
)

_LIB = None


def _candidate_libs() -> list[Path]:
    env_path = os.getenv("ZPE_IOT_NATIVE_LIB")
    candidates: list[Path] = []
    if env_path:
        candidates.append(Path(env_path))

    root = Path(__file__).resolve().parents[2]
    target_root = root / "core" / "target"
    triples = [
        "",
        "x86_64-apple-darwin",
        "aarch64-apple-darwin",
        "x86_64-unknown-linux-gnu",
        "aarch64-unknown-linux-gnu",
    ]
    for triple in triples:
        for profile in ("release", "debug"):
            base = target_root / profile if not triple else target_root / triple / profile
            candidates.extend(
                [
                    base / "libzpe_iot.dylib",
                    base / "libzpe_iot.so",
                    base / "zpe_iot.dll",
                ]
            )
    return candidates


def _load_lib():
    global _LIB
    if _LIB is not None:
        return _LIB

    for candidate in _candidate_libs():
        if candidate.exists():
            try:
                _LIB = _FFI.dlopen(str(candidate))
                return _LIB
            except OSError:
                # Keep scanning in case another target triple matches this interpreter.
                continue
    return None


def available() -> bool:
    return _load_lib() is not None


def _to_c_config(config: Config):
    mode_map = {Mode.FAST: 0, Mode.BALANCED: 1, Mode.LOSSLESS_DELTA: 2}
    return _FFI.new(
        "zpe_iot_config_t*",
        {
            "mode": mode_map[Mode(config.mode)],
            "threshold": float(config.threshold),
            "step": float(config.step),
            "bands0": float(config.bands[0]),
            "bands1": float(config.bands[1]),
            "bands2": float(config.bands[2]),
            "adaptive": 1 if config.adaptive else 0,
            "thr_min": float(config.thr_min),
            "thr_max": float(config.thr_max),
            "alpha": float(config.alpha),
            "k": float(config.k),
            "preset_id": int(config.preset_id),
        },
    )


def _sample_count_from_packet(packet: bytes) -> int:
    if len(packet) < 6:
        return 0
    return int.from_bytes(packet[4:6], "little")


def encode(samples: np.ndarray, config: Optional[Config] = None) -> bytes:
    lib = _load_lib()
    if lib is None:
        raise RuntimeError("zpe-iot native library not found")

    x = np.asarray(samples, dtype=np.float64)
    if x.ndim != 1:
        raise ValueError("samples must be a 1D array")
    cfg = config or Config()

    in_buf = _FFI.new("double[]", x.tolist())
    # generous output capacity to avoid retries
    out_cap = max(256, x.size * 4)
    out_buf = _FFI.new("uint8_t[]", out_cap)

    n = lib.zpe_iot_encode(in_buf, x.size, _to_c_config(cfg), out_buf, out_cap)
    if n < 0:
        raise RuntimeError(f"native encode failed with status={n}")

    return bytes(_FFI.buffer(out_buf, n))


def decode(packet: bytes) -> np.ndarray:
    lib = _load_lib()
    if lib is None:
        raise RuntimeError("zpe-iot native library not found")

    sample_count = _sample_count_from_packet(packet)
    if sample_count <= 0:
        return np.array([], dtype=np.float64)

    in_buf = _FFI.new("uint8_t[]", packet)
    out_buf = _FFI.new("double[]", sample_count)
    n = lib.zpe_iot_decode(in_buf, len(packet), out_buf, sample_count)
    if n < 0:
        raise RuntimeError(f"native decode failed with status={n}")

    return np.frombuffer(_FFI.buffer(out_buf, n * 8), dtype=np.float64).copy()
