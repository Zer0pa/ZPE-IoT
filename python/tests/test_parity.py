import numpy as np
import pytest

from zpe_iot import Config, decode, encode
from zpe_iot import _native


@pytest.mark.skipif(not _native.available(), reason="Native library unavailable")
def test_python_rust_parity_100_vectors():
    rng = np.random.default_rng(123)
    cfg = Config.from_preset("vibration")

    for _ in range(100):
        x = rng.standard_normal(256).astype(np.float64)
        py_packet = encode(x, config=cfg).to_bytes()
        native_packet = _native.encode(x, config=cfg)
        assert py_packet == native_packet


@pytest.mark.skipif(not _native.available(), reason="Native library unavailable")
@pytest.mark.parametrize(
    ("wi1_enabled", "zh1_enabled"),
    [
        (True, False),
        (False, True),
        (True, True),
    ],
)
def test_python_rust_parity_with_experimental_wrappers(
    monkeypatch: pytest.MonkeyPatch,
    wi1_enabled: bool,
    zh1_enabled: bool,
) -> None:
    monkeypatch.setenv("ZPE_IOT_WI1_ENTROPY_STAGE", "1" if wi1_enabled else "0")
    monkeypatch.setenv("ZPE_IOT_ZH1_DERIVATIVE_STAGE", "1" if zh1_enabled else "0")

    rng = np.random.default_rng(456)
    cfg = Config.from_preset("vibration")

    for _ in range(25):
        x = rng.standard_normal(256).astype(np.float64)
        py_packet = encode(x, config=cfg).to_bytes()
        native_packet = _native.encode(x, config=cfg)
        assert py_packet == native_packet
        np.testing.assert_allclose(_native.decode(native_packet), decode(native_packet), rtol=0.0, atol=1e-12)
