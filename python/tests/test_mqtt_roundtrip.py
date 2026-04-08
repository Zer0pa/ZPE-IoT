from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "examples" / "mqtt_integration.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("mqtt_integration_example", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_mqtt_roundtrip_in_memory_publish_path() -> None:
    module = _load_module()
    publisher = module.MemoryPublisher()
    summary = module.roundtrip_with_publisher(publisher, topic="tests/zpe-iot")

    assert len(publisher.messages) == 1
    topic, packet = publisher.messages[0]
    assert topic == "tests/zpe-iot"
    restored = module.decode_sensor_packet(packet)

    assert restored.shape[0] == summary["sample_count"]
    assert summary["packet_bytes"] == len(packet)
    assert summary["compression_ratio"] > 1.0
    assert summary["nrmse"] < 0.1
