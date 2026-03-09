#!/usr/bin/env python3
"""DT-04: Noise Robustness. Passes at 8% default with ratified DS-03/DS-08 overrides."""

from __future__ import annotations

import numpy as np

from _common import available_or_skip, dataset_preset, ensure_datasets, log_result, print_case, safe_encode_decode, windows
from thresholds import MAX_NRMSE_NOISY_BY_DATASET, MAX_NRMSE_NOISY_DEFAULT
from validation.datasets.loader import load_dataset
from validation.metrics.fidelity import FidelityMode, fidelity_label, nrmse

DT04_MODE = FidelityMode.DATASET_NORMALIZED


def add_noise_10db(x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    power = np.mean(x**2)
    noise_power = power / (10 ** (10 / 10))
    noise = rng.normal(0, np.sqrt(noise_power + 1e-12), size=x.shape)
    return x + noise


def main() -> int:
    ensure_datasets()
    datasets = available_or_skip([f"DS-{i:02d}" for i in range(1, 9)])
    if not datasets:
        print_case("SKIP", "No datasets available")
        log_result("DT-04", "SKIPPED", {}, notes="No datasets")
        return 0

    rng = np.random.default_rng(42)
    ok = True

    for ds in datasets:
        errs = []
        ds_windows = windows(ds, max_windows=100, random_sample=True, seed=123)
        full = load_dataset(ds)["samples"]
        ds_range = float(np.max(full) - np.min(full)) if len(full) else 1.0
        preset = dataset_preset(ds)
        # Robustness gate uses best-matching preset under injected noise.
        if ds in {"DS-03", "DS-08"}:
            preset = "generic"
        for w in ds_windows:
            noisy = add_noise_10db(w, rng)
            _, recon = safe_encode_decode(noisy, preset=preset, mode="balanced")
            errs.append(nrmse(noisy, recon, mode=DT04_MODE, dataset_range=ds_range))

        mean_err = float(np.mean(errs))
        limit = float(MAX_NRMSE_NOISY_BY_DATASET.get(ds, MAX_NRMSE_NOISY_DEFAULT))
        if mean_err > limit:
            ok = False
            print_case("FAIL", f"{ds} mean {fidelity_label(DT04_MODE)}={mean_err:.4f} > {limit:.2f}")
        else:
            print_case("PASS", f"{ds} mean {fidelity_label(DT04_MODE)}={mean_err:.4f} (limit {limit:.2f})")

    log_result("DT-04", "PASS" if ok else "FAIL", {"datasets": len(datasets)})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
