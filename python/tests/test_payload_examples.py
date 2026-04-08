from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_module(name: str):
    path = REPO_ROOT / "examples" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_lorawan_payload_stays_within_dr0_budget() -> None:
    module = _load_module("lorawan_payload")
    summary = module.summarize_lorawan_payload()

    assert summary["fits_budget"] is True
    assert summary["packet_bytes"] <= module.MAX_LORAWAN_DR0_BYTES
    assert summary["compression_ratio"] > 1.0
    assert summary["nrmse"] < 0.1


def test_ble_payload_stays_within_advertising_budget() -> None:
    module = _load_module("ble_beacon")
    summary = module.summarize_ble_payload()

    assert summary["fits_budget"] is True
    assert summary["packet_bytes"] <= module.MAX_BLE_ADV_BYTES
    assert summary["compression_ratio"] > 1.0
    assert summary["nrmse"] < 0.1
