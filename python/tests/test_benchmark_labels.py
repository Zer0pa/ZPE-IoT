from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.benchmarks.run_benchmarks import _summary_payload


def test_pt6_label_not_available_when_total_zero() -> None:
    payload = _summary_payload([], "E2", "20260214T000000", "sha", {})
    assert payload["total"] == 0
    assert payload["pt6_status"] == "NOT_AVAILABLE"
    assert payload["pt6_label"] == "NOT_AVAILABLE"


def test_pt6_label_by_evidence_tier_when_data_exists() -> None:
    rows = [
        {
            "dataset": "DS-01",
            "zpe_iot_cr": 5.0,
            "zpe_iot_nrmse": 0.01,
            "zstd_cr": 3.0,
            "lz4_cr": 2.0,
            "zlib_cr": 3.5,
            "gorilla_cr": 2.5,
            "winner": "zpe-iot",
        }
    ]
    e0 = _summary_payload(rows, "E0", "20260214T000000", "sha", {})
    e1 = _summary_payload(rows, "E1", "20260214T000000", "sha", {})

    assert e0["pt6_label"] == "PROVISIONAL"
    assert e1["pt6_label"] == "FINAL"
