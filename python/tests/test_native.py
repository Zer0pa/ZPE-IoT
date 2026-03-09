from __future__ import annotations

import numpy as np
import pytest

from zpe_iot import Config
from zpe_iot import _native


def _force_no_library(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_native, "_LIB", None)
    monkeypatch.setattr(_native, "_candidate_libs", lambda: [])


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
