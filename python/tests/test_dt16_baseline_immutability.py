from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "validation" / "destruct_tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "validation" / "destruct_tests"))

from validation.destruct_tests import dt16_benchmark_regression as dt16


def test_dt16_fails_on_baseline_hash_mismatch(tmp_path: Path, monkeypatch) -> None:
    baseline_root = tmp_path / "baseline"
    tag = "unit_test_tag"
    baseline_dir = baseline_root / tag
    baseline_dir.mkdir(parents=True)

    baseline_summary = baseline_dir / "bench_summary.json"
    baseline_summary.write_text(json.dumps({"mean_cr": 4.0}), encoding="utf-8")
    (baseline_dir / "manifest.json").write_text(
        json.dumps({"bench_summary_sha256": "0" * 64}),
        encoding="utf-8",
    )

    current_summary = tmp_path / "bench_summary_20260219T000000.json"
    current_summary.write_text(json.dumps({"mean_cr": 4.0}), encoding="utf-8")

    monkeypatch.setattr(dt16, "BASELINE_ROOT", baseline_root)
    monkeypatch.setattr(dt16, "ACTIVE_TAG_FILE", baseline_root / "ACTIVE_BASELINE_TAG")
    monkeypatch.setattr(dt16, "_latest", lambda _pattern: current_summary)
    monkeypatch.setenv("ZPE_IOT_BASELINE_TAG", tag)
    monkeypatch.setattr(sys, "argv", ["dt16_benchmark_regression.py"])

    assert dt16.main() == 1
