from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.benchmarks.run_benchmarks import _summary_payload


def _rows(total: int) -> list[dict]:
    if total <= 0:
        return []
    return [
        {
            "dataset": f"DS-{i + 1:02d}",
            "zpe_iot_cr": 5.0,
            "zpe_iot_nrmse": 0.01,
            "zstd_cr": 3.0,
            "lz4_cr": 2.0,
            "zlib_cr": 3.2,
            "gorilla_cr": 2.1,
            "winner": "zpe-iot",
        }
        for i in range(total)
    ]


def test_benchmark_label_golden_cases() -> None:
    fixture = Path(__file__).with_name("fixtures") / "benchmark_label_cases.json"
    cases = json.loads(fixture.read_text(encoding="utf-8"))

    for case in cases:
        payload = _summary_payload(
            _rows(int(case["total"])),
            str(case["evidence_class"]),
            "20260219T000000",
            "sha",
            {},
        )
        assert payload["pt6_label"] == case["expected_label"], case["name"]
        assert payload["pt6_status"] == case["expected_status"], case["name"]
