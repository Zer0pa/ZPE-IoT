from __future__ import annotations

import numpy as np
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.benchmarks._common import BENCHMARK_FIDELITY_MODE
from validation.benchmarks.run_benchmarks import _summary_payload
from validation.metrics.fidelity import FidelityMode, fidelity_label, nrmse


def test_fidelity_labels_are_explicit() -> None:
    assert fidelity_label(FidelityMode.WINDOW_NORMALIZED) == "NRMSE(window-normalized)"
    assert fidelity_label(FidelityMode.DATASET_NORMALIZED) == "NRMSE(dataset-normalized)"


def test_dataset_normalized_nrmse_uses_dataset_range() -> None:
    x = np.array([0.0, 0.0, 1.0, 1.0], dtype=np.float64)
    y = np.array([0.0, 0.0, 0.5, 0.5], dtype=np.float64)

    window_value = nrmse(x, y, mode=FidelityMode.WINDOW_NORMALIZED)
    dataset_value = nrmse(x, y, mode=FidelityMode.DATASET_NORMALIZED, dataset_range=10.0)
    assert window_value > dataset_value


def test_benchmark_summary_carries_named_fidelity_mode() -> None:
    rows = [
        {
            "dataset": "DS-01",
            "zpe_iot_cr": 4.0,
            "zpe_iot_nrmse": 0.01,
            "zstd_cr": 3.0,
            "lz4_cr": 2.0,
            "zlib_cr": 3.2,
            "gorilla_cr": 2.1,
            "winner": "zpe-iot",
        }
    ]
    payload = _summary_payload(rows, "E1", "20260219T000000", "sha", {})
    assert payload["fidelity_metric_mode"] == BENCHMARK_FIDELITY_MODE.value
    assert payload["fidelity_metric_label"] == fidelity_label(BENCHMARK_FIDELITY_MODE)
