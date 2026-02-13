"""Compress sensor readings before publishing to MQTT."""

from __future__ import annotations

import json
import time

import numpy as np
import zpe_iot

try:
    import paho.mqtt.client as mqtt
except Exception:  # soft dependency
    mqtt = None


BROKER = "localhost"
TOPIC = "sensors/compressed"


def make_payload() -> bytes:
    t = np.linspace(0, 1, 256)
    signal = np.sin(2 * np.pi * 30 * t) + 0.1 * np.random.randn(256)
    return zpe_iot.encode(signal, preset="vibration").to_bytes()


def run() -> None:
    if mqtt is None:
        print("paho-mqtt not installed. Install with: pip install paho-mqtt")
        return

    client = mqtt.Client()
    client.connect(BROKER)

    for _ in range(3):
        packet = make_payload()
        client.publish(TOPIC, packet)
        print(f"Published {len(packet)} bytes to {TOPIC}")
        time.sleep(1)

    client.disconnect()


if __name__ == "__main__":
    run()
