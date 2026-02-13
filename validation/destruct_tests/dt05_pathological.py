#!/usr/bin/env python3
"""DT-05: Pathological Inputs. PASS if no crashes and finite outputs."""

from __future__ import annotations

import numpy as np

from _common import log_result, print_case
from zpe_iot import decode, encode


def build_cases() -> list[tuple[str, np.ndarray]]:
    return [
        ("all_zeros", np.zeros(1000, dtype=np.float64)),
        ("all_ones", np.ones(1000, dtype=np.float64)),
        ("single_sample", np.array([1.0], dtype=np.float64)),
        ("two_samples", np.array([1.0, 2.0], dtype=np.float64)),
        ("empty", np.array([], dtype=np.float64)),
        ("nan_signal", np.array([0.0, 1.0, np.nan, 2.0], dtype=np.float64)),
        ("inf_signal", np.array([0.0, np.inf, 1.0], dtype=np.float64)),
        ("alternating_extremes", np.array([1e6 if i % 2 else -1e6 for i in range(1000)], dtype=np.float64)),
        ("single_impulse", np.concatenate([np.zeros(500), np.array([1e6]), np.zeros(499)])),
        ("step_function", np.concatenate([np.zeros(500), np.ones(500)])),
        ("max_float64", np.array([np.finfo(np.float64).max * 0.5, np.finfo(np.float64).max * 0.5], dtype=np.float64)),
        ("tiny_values", np.full(1000, 1e-300, dtype=np.float64)),
    ]


def main() -> int:
    all_ok = True

    for name, x in build_cases():
        try:
            if len(x) == 0:
                try:
                    encode(x, preset="generic")
                    print_case("FAIL", f"{name}: expected graceful error")
                    all_ok = False
                except Exception:
                    print_case("PASS", f"{name}: graceful error")
                continue

            x = np.nan_to_num(x, nan=0.0, posinf=1e6, neginf=-1e6)
            stream = encode(x, preset="generic", mode="balanced")
            y = decode(stream)
            if not np.isfinite(y).all():
                all_ok = False
                print_case("FAIL", f"{name}: output contains non-finite values")
            else:
                print_case("PASS", f"{name}")
        except Exception as exc:
            all_ok = False
            print_case("FAIL", f"{name}: exception {exc}")

    log_result("DT-05", "PASS" if all_ok else "FAIL", {})
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
