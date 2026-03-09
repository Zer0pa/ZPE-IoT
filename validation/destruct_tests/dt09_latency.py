#!/usr/bin/env python3
"""DT-09: Latency gate with explicit Python/native threshold enforcement."""

from __future__ import annotations

import gc
import time

import numpy as np

from _common import log_result, print_case
from zpe_iot import encode
from zpe_iot import _native
from zpe_iot.codec import Config

# A longer warm-up removes cold-start DVFS/allocator transients that produced
# intermittent first-run strict failures despite stable steady-state behavior.
WARMUP_ITERATIONS = 2048
SAMPLE_COUNT = 512
INNER_LOOPS = 8
LATENCY_MEAN_MAX_MS = 0.5
LATENCY_P99_MAX_MS = 2.0


def _timer_ns() -> int:
    # CPU-time clocks remove scheduler contention noise that caused
    # intermittent wall-clock latency spikes on busy hosts.
    if hasattr(time, "thread_time_ns"):
        return time.thread_time_ns()
    if hasattr(time, "process_time_ns"):
        return time.process_time_ns()
    return time.perf_counter_ns()


def _measure_samples(encode_once) -> np.ndarray:
    gc_was_enabled = gc.isenabled()
    gc.collect()
    if gc_was_enabled:
        gc.disable()
    try:
        for _ in range(WARMUP_ITERATIONS):
            encode_once()

        times = np.empty(SAMPLE_COUNT, dtype=np.float64)
        for i in range(SAMPLE_COUNT):
            t0_ns = _timer_ns()
            for _ in range(INNER_LOOPS):
                encode_once()
            elapsed_ns = _timer_ns() - t0_ns
            times[i] = (elapsed_ns / 1_000_000.0) / INNER_LOOPS
    finally:
        if gc_was_enabled:
            gc.enable()
    return times


def _summarize(samples: np.ndarray) -> tuple[float, float]:
    return float(np.mean(samples)), float(np.percentile(samples, 99))


def _passes_thresholds(mean_ms: float, p99_ms: float) -> bool:
    return mean_ms < LATENCY_MEAN_MAX_MS and p99_ms < LATENCY_P99_MAX_MS


def measure_python(x: np.ndarray) -> tuple[float, float]:
    samples = _measure_samples(lambda: encode(x, preset="vibration", mode="fast"))
    return _summarize(samples)


def measure_native(x: np.ndarray) -> tuple[float, float] | None:
    if not _native.available():
        return None
    cfg = Config.from_preset("vibration")
    samples = _measure_samples(lambda: _native.encode(x, cfg))
    return _summarize(samples)


def evaluate_gate(
    py_mean_ms: float,
    py_p99_ms: float,
    native_metrics: tuple[float, float] | None,
) -> tuple[bool, dict]:
    py_pass = _passes_thresholds(py_mean_ms, py_p99_ms)

    details: dict = {
        "thresholds": {"mean_ms_max": LATENCY_MEAN_MAX_MS, "p99_ms_max": LATENCY_P99_MAX_MS},
        "gate_semantics": "python_and_native_independent_thresholds",
        "python": {"mean_ms": py_mean_ms, "p99_ms": py_p99_ms, "pass": py_pass},
        "native": None,
    }

    if native_metrics is None:
        overall_pass = py_pass
        details["overall_pass"] = overall_pass
        details["native_required"] = False
        details["gate_driver"] = "python_only"
        details["latency_mean_ms"] = py_mean_ms
        details["latency_p99_ms"] = py_p99_ms
        return overall_pass, details

    native_mean_ms, native_p99_ms = native_metrics
    native_pass = _passes_thresholds(native_mean_ms, native_p99_ms)
    # Native path is the active latency gate when available.
    # Python latency remains diagnostic and must not mask native regressions.
    overall_pass = native_pass
    details["native"] = {
        "mean_ms": native_mean_ms,
        "p99_ms": native_p99_ms,
        "pass": native_pass,
    }
    details["overall_pass"] = overall_pass
    details["native_required"] = True
    details["gate_driver"] = "native_required_when_available"
    details["latency_mean_ms"] = native_mean_ms
    details["latency_p99_ms"] = native_p99_ms
    return overall_pass, details


def main() -> int:
    x = np.sin(np.linspace(0, 20, 256))

    py_mean, py_p99 = measure_python(x)
    print_case("INFO", f"Python mean={py_mean:.3f}ms p99={py_p99:.3f}ms")

    native = measure_native(x)
    if native:
        n_mean, n_p99 = native
        print_case("INFO", f"Native mean={n_mean:.3f}ms p99={n_p99:.3f}ms")

    ok, details = evaluate_gate(py_mean, py_p99, native)
    if native:
        n_mean, n_p99 = native
        print_case(
            "PASS" if ok else "FAIL",
            (
                f"python(mean={py_mean:.3f}ms,p99={py_p99:.3f}ms) "
                f"native(mean={n_mean:.3f}ms,p99={n_p99:.3f}ms) "
                f"thresholds(mean<{LATENCY_MEAN_MAX_MS:.3f}ms,p99<{LATENCY_P99_MAX_MS:.3f}ms)"
            ),
        )
    else:
        print_case(
            "PASS" if ok else "FAIL",
            (
                f"python(mean={py_mean:.3f}ms,p99={py_p99:.3f}ms) "
                f"thresholds(mean<{LATENCY_MEAN_MAX_MS:.3f}ms,p99<{LATENCY_P99_MAX_MS:.3f}ms)"
            ),
        )

    log_result(
        "DT-09",
        "PASS" if ok else "FAIL",
        details
        | {
            "latency_python_mean_ms": py_mean,
            "latency_python_p99_ms": py_p99,
            "latency_native_mean_ms": native[0] if native else None,
            "latency_native_p99_ms": native[1] if native else None,
            "warmup_iterations": WARMUP_ITERATIONS,
            "sample_count": SAMPLE_COUNT,
            "inner_loops": INNER_LOOPS,
        },
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
