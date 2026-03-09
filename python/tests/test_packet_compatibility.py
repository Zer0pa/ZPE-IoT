from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from zpe_iot import compute_nrmse, decode, encode
from zpe_iot.codec import PACKET_VERSION, _crc16_ccitt

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "golden_packets_v1.json"


def _signal(spec: dict) -> np.ndarray:
    kind = spec["type"]
    length = int(spec["length"])
    t = np.arange(length, dtype=np.float64)

    if kind == "sine_mix":
        return np.sin(t * float(spec["freq_a"])) + float(spec["amp_b"]) * np.cos(t * float(spec["freq_b"]))
    if kind == "poly_wave":
        period = int(spec["period"])
        denom = max(1.0, period // 2)
        return ((t % period) - period // 2) / denom + float(spec["sin_amp"]) * np.sin(t * float(spec["sin_freq"]))
    raise ValueError(f"Unsupported fixture signal type: {kind}")


def _mutate_version(packet: bytes, version: int) -> bytes:
    patched = bytearray(packet)
    patched[2] = int(version) & 0xFF
    patched[-2:] = _crc16_ccitt(bytes(patched[:-2])).to_bytes(2, "little")
    return bytes(patched)


def _corrupt_crc(packet: bytes) -> bytes:
    patched = bytearray(packet)
    patched[-1] ^= 0xFF
    return bytes(patched)


def test_golden_packet_bytes_and_roundtrip_stability() -> None:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert payload["packet_version"] == PACKET_VERSION

    for fixture in payload["fixtures"]:
        signal = _signal(fixture["signal"])
        packet = encode(signal, preset=fixture["preset"], mode=fixture["mode"]).to_bytes()
        assert packet.hex() == fixture["packet_hex"]

        restored = decode(bytes.fromhex(fixture["packet_hex"]))
        assert restored.shape[0] == signal.shape[0]

        nrmse = compute_nrmse(signal, restored)
        assert nrmse <= float(fixture["max_nrmse"])


def test_decode_rejects_strict_malformed_packets() -> None:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    reference = bytes.fromhex(payload["fixtures"][0]["packet_hex"])
    bad_magic = bytearray(reference)
    bad_magic[0] ^= 0xFF

    malformed_cases = [
        b"",
        b"\x00\x01",
        b"bad-packet",
        reference[:7],
        bytes(bad_magic),
        _corrupt_crc(reference),
    ]

    for idx, packet in enumerate(malformed_cases):
        with pytest.raises(ValueError, match="Packet|Bad|CRC|Unsupported"):
            decode(packet)


def test_upgrade_backward_packet_version_assertions() -> None:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    for fixture in payload["fixtures"]:
        packet = bytes.fromhex(fixture["packet_hex"])
        restored = decode(packet)
        assert restored.shape[0] == int(fixture["signal"]["length"])

    newer = _mutate_version(bytes.fromhex(payload["fixtures"][0]["packet_hex"]), PACKET_VERSION + 1)
    with pytest.raises(ValueError, match="Unsupported packet version"):
        decode(newer)
