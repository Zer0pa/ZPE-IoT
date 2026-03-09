from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def _load_dt09_module():
    root = Path(__file__).resolve().parents[2]
    dt_dir = root / "validation" / "destruct_tests"
    for p in (dt_dir, root, root / "python"):
        p_str = str(p)
        if p_str not in sys.path:
            sys.path.insert(0, p_str)
    dt09_path = root / "validation" / "destruct_tests" / "dt09_latency.py"
    spec = importlib.util.spec_from_file_location("dt09_latency", dt09_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dt09 = _load_dt09_module()


def test_python_only_passes_when_python_meets_thresholds():
    ok, details = dt09.evaluate_gate(0.1, 1.0, None)
    assert ok
    assert details["native_required"] is False
    assert details["python"]["pass"] is True


def test_python_only_fails_when_python_exceeds_thresholds():
    ok, details = dt09.evaluate_gate(0.9, 2.5, None)
    assert not ok
    assert details["native_required"] is False
    assert details["python"]["pass"] is False


def test_native_failure_is_not_masked_by_python_pass():
    ok, details = dt09.evaluate_gate(0.2, 1.0, (0.7, 1.2))
    assert not ok
    assert details["python"]["pass"] is True
    assert details["native"]["pass"] is False


def test_python_failure_does_not_fail_when_native_passes():
    ok, details = dt09.evaluate_gate(0.8, 1.2, (0.2, 0.5))
    assert ok
    assert details["python"]["pass"] is False
    assert details["native"]["pass"] is True
    assert details["latency_mean_ms"] == 0.2
