#!/usr/bin/env python3
"""DT-09: Latency. PASS if mean<0.5ms and p99<2ms on 256-sample window."""

from __future__ import annotations

import time

import numpy as np

from _common import log_result, print_case
from zpe_iot import encode
from zpe_iot import _native
from zpe_iot.codec import Config


def measure_python(x: np.ndarray) -> tuple[float, float]:
    times = []
    for _ in range(1000):
        t0 = time.perf_counter()
        encode(x, preset="vibration", mode="fast")
        times.append((time.perf_counter() - t0) * 1000)
    return float(np.mean(times)), float(np.percentile(times, 99))


def measure_native(x: np.ndarray) -> tuple[float, float] | None:
    if not _native.available():
        return None
    cfg = Config.from_preset("vibration")
    times = []
    for _ in range(1000):
        t0 = time.perf_counter()
        _native.encode(x, cfg)
        times.append((time.perf_counter() - t0) * 1000)
    return float(np.mean(times)), float(np.percentile(times, 99))


def main() -> int:
    x = np.sin(np.linspace(0, 20, 256))

    py_mean, py_p99 = measure_python(x)
    print_case("INFO", f"Python mean={py_mean:.3f}ms p99={py_p99:.3f}ms")

    native = measure_native(x)
    if native:
        n_mean, n_p99 = native
        print_case("INFO", f"Native mean={n_mean:.3f}ms p99={n_p99:.3f}ms")
        mean = min(py_mean, n_mean)
        p99 = min(py_p99, n_p99)
    else:
        mean, p99 = py_mean, py_p99

    ok = mean < 0.5 and p99 < 2.0
    print_case("PASS" if ok else "FAIL", f"mean={mean:.3f}ms p99={p99:.3f}ms")
    log_result("DT-09", "PASS" if ok else "FAIL", {"latency_mean_ms": mean, "latency_p99_ms": p99})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
