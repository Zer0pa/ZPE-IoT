import numpy as np
import pytest

from zpe_iot import Config, encode
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
