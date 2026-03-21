from __future__ import annotations

import os
from importlib import import_module
from pathlib import Path
from typing import Optional

import numpy as np
from cffi import FFI

from .codec import (
    Config,
    Mode,
    _maybe_unwrap_wi1,
    _maybe_unwrap_zh1,
    _maybe_wrap_wi1,
    _maybe_wrap_zh1,
)

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
_EXTENSION = None


def _load_extension_module():
    global _EXTENSION
    if _EXTENSION is not None:
        return _EXTENSION

    for module_name in ("zpe_iot._zpe_iot_native", "_zpe_iot_native"):
        try:
            _EXTENSION = import_module(module_name)
            return _EXTENSION
        except Exception:
            continue
    return None


def _candidate_bases(root: Path) -> list[Path]:
    target_root = root / "core" / "target"
    triples = [
        "",
        "x86_64-apple-darwin",
        "aarch64-apple-darwin",
        "x86_64-unknown-linux-gnu",
        "aarch64-unknown-linux-gnu",
    ]
    bases: list[Path] = []
    for triple in triples:
        for profile in ("release", "debug"):
            base = target_root / profile if not triple else target_root / triple / profile
            bases.extend([base, base / "deps"])
    return bases


def _candidate_libs() -> list[Path]:
    env_path = os.getenv("ZPE_IOT_NATIVE_LIB")
    candidates: list[Path] = []
    if env_path:
        candidates.append(Path(env_path))

    root = Path(__file__).resolve().parents[2]
    for base in _candidate_bases(root):
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
    return _load_extension_module() is not None or _load_lib() is not None


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
    packet = _maybe_unwrap_wi1(_maybe_unwrap_zh1(packet))
    if len(packet) < 6:
        return 0
    return int.from_bytes(packet[4:6], "little")


def encode(samples: np.ndarray, config: Optional[Config] = None) -> bytes:
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim != 1:
        raise ValueError("samples must be a 1D array")
    if not x.flags.c_contiguous:
        x = np.ascontiguousarray(x, dtype=np.float64)
    cfg = config or Config()

    ext = _load_extension_module()
    if ext is not None:
        packet = bytes(
            ext.encode_packet(
                x,
                mode={Mode.FAST: 0, Mode.BALANCED: 1, Mode.LOSSLESS_DELTA: 2}[Mode(cfg.mode)],
                threshold=float(cfg.threshold),
                step=float(cfg.step),
                bands=tuple(float(v) for v in cfg.bands),
                adaptive=bool(cfg.adaptive),
                thr_min=float(cfg.thr_min),
                thr_max=float(cfg.thr_max),
                alpha=float(cfg.alpha),
                k=float(cfg.k),
                preset_id=int(cfg.preset_id),
            )
        )
        return _maybe_wrap_zh1(_maybe_wrap_wi1(packet))

    lib = _load_lib()
    if lib is None:
        raise RuntimeError("zpe-iot native library not found")

    # Zero-copy view over NumPy storage avoids per-call list materialization.
    in_buf = _FFI.from_buffer("double[]", x)
    # generous output capacity to avoid retries
    out_cap = max(256, x.size * 4)
    out_raw = bytearray(out_cap)
    out_buf = _FFI.from_buffer("uint8_t[]", out_raw)

    n = lib.zpe_iot_encode(in_buf, x.size, _to_c_config(cfg), out_buf, out_cap)
    if n < 0:
        raise RuntimeError(f"native encode failed with status={n}")

    packet = bytes(out_raw[:n])
    return _maybe_wrap_zh1(_maybe_wrap_wi1(packet))


def decode(packet: bytes) -> np.ndarray:
    ext = _load_extension_module()
    lib = None if ext is not None else _load_lib()
    if ext is None and lib is None:
        raise RuntimeError("zpe-iot native library not found")

    packet = _maybe_unwrap_wi1(_maybe_unwrap_zh1(packet))
    sample_count = _sample_count_from_packet(packet)
    if sample_count <= 0:
        return np.array([], dtype=np.float64)

    if ext is not None:
        return np.asarray(ext.decode_packet(packet), dtype=np.float64)

    in_buf = _FFI.new("uint8_t[]", packet)
    out_buf = _FFI.new("double[]", sample_count)
    n = lib.zpe_iot_decode(in_buf, len(packet), out_buf, sample_count)
    if n < 0:
        raise RuntimeError(f"native decode failed with status={n}")

    return np.frombuffer(_FFI.buffer(out_buf, n * 8), dtype=np.float64).copy()
