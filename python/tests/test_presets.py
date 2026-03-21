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


def test_ratified_preset_values_remain_canonical():
    expected = {
        "temperature": {"mode": "balanced", "threshold": 0.05, "step": 0.0, "bands": (1.0, 2.0, 4.0)},
        "gps_track": {"mode": "balanced", "threshold": 0.001, "step": 0.0, "bands": (1.0, 4.0, 16.0)},
        "flow": {"mode": "balanced", "threshold": 0.05, "step": 0.0, "bands": (1.0, 2.0, 8.0)},
    }

    for preset, values in expected.items():
        cfg = Config.from_preset(preset)
        assert cfg.mode.value == values["mode"]
        assert cfg.threshold == values["threshold"]
        assert cfg.step == values["step"]
        assert cfg.bands == values["bands"]
