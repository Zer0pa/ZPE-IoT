"""MQTT publish demo for ZPE-compressed sensor packets.

Runs in-memory by default so it works from a clean clone.
If `--broker` is provided and `paho-mqtt` is installed, the same packet path
publishes to a live MQTT broker.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from typing import Protocol

import numpy as np
import zpe_iot

try:
    import paho.mqtt.client as mqtt
except Exception:  # pragma: no cover - optional dependency
    mqtt = None


DEFAULT_TOPIC = "sensors/zpe-iot"


class Publisher(Protocol):
    def publish(self, topic: str, payload: bytes) -> None:
        """Publish a payload to a topic."""


@dataclass
class MemoryPublisher:
    messages: list[tuple[str, bytes]] = field(default_factory=list)

    def publish(self, topic: str, payload: bytes) -> None:
        self.messages.append((topic, payload))


def build_sensor_window(sample_count: int = 32) -> np.ndarray:
    t = np.linspace(0.0, 1.0, sample_count, dtype=np.float64)
    return np.sin(2 * np.pi * 5 * t) + 0.05 * np.cos(2 * np.pi * 13 * t)


def encode_sensor_window(samples: np.ndarray, preset: str = "vibration") -> bytes:
    stream = zpe_iot.encode(np.asarray(samples, dtype=np.float64), preset=preset)
    return stream.to_bytes()


def decode_sensor_packet(packet: bytes) -> np.ndarray:
    return zpe_iot.decode(packet)


def roundtrip_with_publisher(publisher: Publisher, topic: str = DEFAULT_TOPIC) -> dict:
    samples = build_sensor_window()
    packet = encode_sensor_window(samples)
    publisher.publish(topic, packet)
    restored = decode_sensor_packet(packet)
    return {
        "topic": topic,
        "sample_count": int(samples.size),
        "packet_bytes": len(packet),
        "compression_ratio": float((samples.size * 8) / max(1, len(packet))),
        "nrmse": float(zpe_iot.compute_nrmse(samples, restored)),
    }


def run_paho_publish(broker: str, topic: str = DEFAULT_TOPIC, port: int = 1883) -> dict:
    if mqtt is None:
        raise RuntimeError("paho-mqtt is not installed")

    client = mqtt.Client()
    client.connect(broker, port)
    summary = roundtrip_with_publisher(client, topic=topic)
    client.disconnect()
    summary["transport"] = "paho-mqtt"
    summary["broker"] = broker
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--broker", help="Optional MQTT broker hostname")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--topic", default=DEFAULT_TOPIC, help="MQTT topic")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.broker and mqtt is not None:
        summary = run_paho_publish(args.broker, topic=args.topic, port=args.port)
    else:
        publisher = MemoryPublisher()
        summary = roundtrip_with_publisher(publisher, topic=args.topic)
        summary["transport"] = "memory"
        if args.broker and mqtt is None:
            summary["note"] = "paho-mqtt not installed; ran in-memory publish path instead"
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
