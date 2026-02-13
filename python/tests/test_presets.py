import numpy as np

from zpe_iot import Config, Preset, decode, encode


def test_all_presets_instantiate_and_roundtrip():
    t = np.linspace(0, 1, 512)
    x = np.sin(2 * np.pi * 5 * t)

    for preset in Preset:
        cfg = Config.from_preset(preset.value)
        stream = encode(x, config=cfg)
        y = decode(stream)
        assert len(y) == len(x)
