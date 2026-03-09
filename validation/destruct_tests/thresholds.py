"""Threshold constants used by DT gates.

This file is the local code source-of-truth aligned with PRD constants/addenda.
"""

MAX_NRMSE = 0.05
MAX_NRMSE_NOISY_DEFAULT = 0.08
MAX_NRMSE_NOISY_BY_DATASET = {
    "DS-03": 0.12,
    "DS-08": 0.14,
}

ADAPTIVE_THR_MIN = 0.001
ADAPTIVE_THR_MAX = 1.0

PRESET_MIN_MEAN_CR = 3.8
PRESET_MAX_MEAN_NRMSE = 0.05

BENCHMARK_REGRESSION_MAX_DEGRADATION = 0.05
WI1_MIN_CR_GAIN = 0.12
ZH1_MIN_CR_GAIN = 0.08
