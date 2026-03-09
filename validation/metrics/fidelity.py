from __future__ import annotations

from enum import Enum

import numpy as np


class FidelityMode(str, Enum):
    WINDOW_NORMALIZED = "window-normalized"
    DATASET_NORMALIZED = "dataset-normalized"


def fidelity_label(mode: FidelityMode) -> str:
    if mode == FidelityMode.WINDOW_NORMALIZED:
        return "NRMSE(window-normalized)"
    return "NRMSE(dataset-normalized)"


def nrmse(
    original: np.ndarray,
    reconstructed: np.ndarray,
    *,
    mode: FidelityMode,
    dataset_range: float | None = None,
) -> float:
    x = np.asarray(original, dtype=np.float64).reshape(-1)
    y = np.asarray(reconstructed, dtype=np.float64).reshape(-1)
    n = min(x.size, y.size)
    if n == 0:
        return 0.0

    x = x[:n]
    y = y[:n]
    mse = float(np.mean((x - y) ** 2))

    if mode == FidelityMode.DATASET_NORMALIZED and dataset_range is not None:
        denom = float(dataset_range)
    else:
        denom = float(np.max(x) - np.min(x))

    if denom <= 1e-12:
        return 0.0 if mse <= 1e-12 else 1.0

    return float(np.sqrt(mse) / denom)
