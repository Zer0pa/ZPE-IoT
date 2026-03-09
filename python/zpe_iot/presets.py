from __future__ import annotations

from enum import Enum
from typing import Dict


class Preset(str, Enum):
    TEMPERATURE = "temperature"
    VIBRATION = "vibration"
    ACCELEROMETER = "accelerometer"
    PRESSURE = "pressure"
    GPS_TRACK = "gps_track"
    VOLTAGE = "voltage"
    CURRENT = "current"
    FLOW = "flow"
    GENERIC = "generic"


PRESET_CONFIGS: Dict[str, dict] = {
    "temperature": {
        "mode": "balanced",
        "threshold": 0.05,
        "step": 0.0,
        "bands": (1.0, 2.0, 4.0),
        "preset_id": 0,
    },
    "vibration": {
        "mode": "balanced",
        "threshold": 0.02,
        "step": 0.01,
        "bands": (1.0, 4.0, 16.0),
        "preset_id": 1,
    },
    "accelerometer": {
        "mode": "balanced",
        "threshold": 0.03,
        "step": 0.01,
        "bands": (1.0, 4.0, 16.0),
        "preset_id": 2,
    },
    "pressure": {
        "mode": "balanced",
        "threshold": 0.01,
        "step": 0.1,
        "bands": (1.0, 2.0, 8.0),
        "preset_id": 3,
    },
    "gps_track": {
        "mode": "balanced",
        "threshold": 0.001,
        "step": 0.0,
        "bands": (1.0, 4.0, 16.0),
        "preset_id": 4,
    },
    "voltage": {
        "mode": "balanced",
        "threshold": 0.02,
        "step": 0.01,
        "bands": (1.0, 4.0, 16.0),
        "preset_id": 5,
    },
    "current": {
        "mode": "balanced",
        "threshold": 0.02,
        "step": 0.01,
        "bands": (1.0, 4.0, 16.0),
        "preset_id": 6,
    },
    "flow": {
        "mode": "balanced",
        "threshold": 0.05,
        "step": 0.0,
        "bands": (1.0, 2.0, 8.0),
        "preset_id": 7,
    },
    "generic": {
        "mode": "balanced",
        "threshold": 0.05,
        "step": 0.0,
        "bands": (1.0, 4.0, 16.0),
        "preset_id": 8,
    },
}


def preset_config(preset: str | Preset) -> dict:
    name = preset.value if isinstance(preset, Preset) else str(preset).lower()
    if name not in PRESET_CONFIGS:
        raise ValueError(f"Unknown preset: {preset}")
    return dict(PRESET_CONFIGS[name])


def all_presets() -> list[str]:
    return list(PRESET_CONFIGS.keys())
