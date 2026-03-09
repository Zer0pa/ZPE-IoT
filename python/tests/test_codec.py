import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

import zpe_iot


def _arr(values):
    return np.asarray(values, dtype=np.float64)


@given(st.lists(st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False), min_size=32, max_size=256))
@settings(max_examples=60, deadline=None)
def test_determinism(values):
    x = _arr(values)
    a = zpe_iot.encode(x, preset="generic").to_bytes()
    b = zpe_iot.encode(x, preset="generic").to_bytes()
    assert a == b


@given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=32, max_size=256))
@settings(max_examples=40, deadline=None)
def test_roundtrip_length_and_finite(values):
    x = _arr(values)
    stream = zpe_iot.encode(x, preset="generic")
    y = zpe_iot.decode(stream)
    assert len(y) == len(x)
    assert np.isfinite(y).all()


def test_fidelity_on_smooth_signal():
    t = np.linspace(0, 2 * np.pi, 1024)
    x = np.sin(5 * t) + 0.2 * np.sin(13 * t)
    stream = zpe_iot.encode(x, preset="vibration", mode="balanced", adaptive=True)
    y = zpe_iot.decode(stream)
    assert zpe_iot.compute_nrmse(x, y) < 0.05


def test_compression_never_expands_baseline_signal():
    t = np.linspace(0, 4 * np.pi, 1024)
    x = np.sin(t)
    stream = zpe_iot.encode(x, preset="generic")
    assert stream.compression_ratio > 1.0


def test_monotonicity_threshold_vs_cr():
    rng = np.random.default_rng(42)
    x = np.sin(np.linspace(0, 20, 1024)) + 0.1 * rng.standard_normal(1024)

    thresholds = [0.001, 0.005, 0.01, 0.05, 0.1]
    ratios = [zpe_iot.encode(x, preset="vibration", threshold=t).compression_ratio for t in thresholds]

    assert all(ratios[i] <= ratios[i + 1] + 1e-9 for i in range(len(ratios) - 1))


def test_wi1_entropy_stage_roundtrip(monkeypatch):
    x = np.repeat(np.sin(np.linspace(0, 8 * np.pi, 1024)), 2)
    monkeypatch.setenv("ZPE_IOT_WI1_ENTROPY_STAGE", "1")
    packet = zpe_iot.encode(x, preset="generic").to_bytes()
    y = zpe_iot.decode(packet)

    assert len(y) == len(x)
    assert np.isfinite(y).all()


def test_zh1_derivative_stage_roundtrip(monkeypatch):
    x = np.sin(np.linspace(0, 16 * np.pi, 2048)) + 0.1 * np.sin(np.linspace(0, 64 * np.pi, 2048))
    monkeypatch.setenv("ZPE_IOT_ZH1_DERIVATIVE_STAGE", "1")
    packet = zpe_iot.encode(x, preset="voltage").to_bytes()
    y = zpe_iot.decode(packet)

    assert len(y) == len(x)
    assert np.isfinite(y).all()
