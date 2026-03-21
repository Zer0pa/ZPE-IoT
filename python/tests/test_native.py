from __future__ import annotations

import numpy as np
import pytest

from zpe_iot import Config
from zpe_iot import _native
from zpe_iot.codec import _maybe_wrap_wi1, _maybe_wrap_zh1


def _force_no_library(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_native, "_LIB", None)
    monkeypatch.setattr(_native, "_EXTENSION", None)
    monkeypatch.setattr(_native, "_candidate_libs", lambda: [])
    monkeypatch.setattr(_native, "_load_extension_module", lambda: None)


def test_native_available_false_without_library(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_no_library(monkeypatch)
    assert _native.available() is False


def test_native_encode_raises_without_library(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_no_library(monkeypatch)
    with pytest.raises(RuntimeError, match="native library not found"):
        _native.encode(np.array([0.0, 1.0], dtype=np.float64), Config())


def test_native_decode_raises_without_library(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_no_library(monkeypatch)
    with pytest.raises(RuntimeError, match="native library not found"):
        _native.decode(b"\x00\x01\x02")


def test_sample_count_from_packet_header() -> None:
    assert _native._sample_count_from_packet(b"\x00\x00\x00\x00\x10\x00") == 16
    assert _native._sample_count_from_packet(b"\x00\x01") == 0


@pytest.mark.parametrize(
    ("env_key", "wrapper"),
    [
        ("ZPE_IOT_WI1_ENTROPY_STAGE", _maybe_wrap_wi1),
        ("ZPE_IOT_ZH1_DERIVATIVE_STAGE", _maybe_wrap_zh1),
    ],
)
def test_sample_count_from_wrapped_packet(
    monkeypatch: pytest.MonkeyPatch,
    env_key: str,
    wrapper,
) -> None:
    packet = b"\x00\x00\x00\x00\x10\x00" + (b"\x00" * 128)
    monkeypatch.setenv(env_key, "1")
    wrapped = wrapper(packet)
    assert wrapped != packet
    assert _native._sample_count_from_packet(wrapped) == 16


def test_candidate_libs_include_deps_directories() -> None:
    candidates = {path.as_posix() for path in _native._candidate_libs()}
    assert any(path.endswith("/core/target/release/deps/libzpe_iot.dylib") for path in candidates)
    assert any(path.endswith("/core/target/debug/deps/libzpe_iot.dylib") for path in candidates)
