# RUNBOOK_02_FALSIFICATION.md — Phase 2: Full Falsification Harness

**STOP.** Have you read `RUNBOOK_00_MASTER.md`? If no, read it NOW.
**Is Phase 1 marked `PASSED` in the Phase Gates table?** If no, go back to `RUNBOOK_01`.

---

## Phase 2 Objective

Download all benchmark datasets, run the complete falsification harness (all 16 DTs from PRD §5.2) on real-world sensor data, establish baseline metrics, and prove the codec is CORRECT and COMMERCIALLY VIABLE — not just functional.

**Input:** Working Rust codec + Python reference from Phase 1
**Output:** All P0+P1 DTs passing on real datasets, Pareto frontiers documented, baseline established
**Gating DTs:** ALL P0 + ALL P1
**Duration:** ~8 days

---

## Step 0: Dataset Acquisition

### Step 0.1: Create Dataset Downloader

- [x] **Action:** Create `validation/datasets/download_datasets.py`.

This script MUST:
- Download all 8 real-world datasets from PRD §4.1 (DS-01..DS-08)
- Generate DS-09 (white noise) and DS-10 (sine sweep) synthetically
- Save each dataset in a standardised format: `validation/datasets/<ds_id>/data.npz`
- Each `.npz` contains: `samples` (float64 array), `sample_rate` (float), `name` (str)
- Log download progress, verify checksums where available
- Skip already-downloaded datasets (idempotent)

```python
DATASETS = {
    "DS-01": {"name": "UCI Gas Sensor Array", "url": "https://archive.ics.uci.edu/ml/machine-learning-databases/00322/"},
    "DS-02": {"name": "FEMTO Bearing Vibration", "url": "https://ti.arc.nasa.gov/tech/dash/groups/pcoe/prognostic-data-repository/"},
    "DS-03": {"name": "Intel Lab Temperature", "url": "http://db.csail.mit.edu/labdata/labdata.html"},
    "DS-04": {"name": "SHL Locomotion IMU", "url": "http://www.shl-dataset.org/"},
    "DS-05": {"name": "NOAA Weather Hourly", "url": "https://www.ncei.noaa.gov/data/global-hourly/"},
    "DS-06": {"name": "Numenta NAB", "url": "https://github.com/numenta/NAB"},
    "DS-07": {"name": "GeoLife GPS", "url": "https://www.microsoft.com/en-us/download/details.aspx?id=52367"},
    "DS-08": {"name": "DEBS 2012 Manufacturing", "url": "https://debs.org/grand-challenges/2012/"},
    "DS-09": {"name": "Synthetic White Noise", "generated": True},
    "DS-10": {"name": "Synthetic Sine Sweep", "generated": True},
}
```

- [x] **Verify:** `python download_datasets.py` completes. `ls validation/datasets/` shows DS-01..DS-10 directories.

**NOTE:** Some datasets require manual download or registration. For those:
1. Document the manual step in `validation/datasets/README.md`
2. Provide a script that processes the raw download into `.npz` format
3. If a dataset is truly unavailable, mark it `UNAVAILABLE` and proceed with remaining datasets
4. A DT that uses an unavailable dataset gets status `SKIPPED`, not `FAIL`

### Step 0.2: Create Dataset Loader Utility

- [x] **Action:** Create `validation/datasets/loader.py`:
```python
def load_dataset(ds_id: str) -> dict:
    """Load dataset by ID. Returns dict with 'samples', 'sample_rate', 'name'."""
    ...

def list_available_datasets() -> list[str]:
    """Return list of downloaded dataset IDs."""
    ...

def iter_dataset_windows(ds_id: str, window_size: int = 256) -> Iterator:
    """Yield non-overlapping windows from dataset."""
    ...
```

- [x] **Verify:** `load_dataset("DS-09")` returns synthetic noise array.

---

## Step 1: Implement ALL P0 Destruct Tests on Real Data

### Step 1.1: DT-01 — Fidelity Gate

- [x] **Action:** Create `validation/destruct_tests/dt01_fidelity.py`.

```
DT-01: Fidelity Gate
PRD: §5.2, INV-FIDELITY
PASS CONDITION: NRMSE < 5% on EVERY dataset (DS-01..DS-08) in BALANCED mode
                Use best-matching preset per dataset.
EXIT CODE: 0 = PASS, 1 = FAIL

Dataset-to-preset mapping:
  DS-01 → "generic"      (chemical sensors)
  DS-02 → "vibration"    (accelerometer)
  DS-03 → "temperature"  (thermistor)
  DS-04 → "accelerometer" (IMU)
  DS-05 → "pressure"     (barometric, approximate)
  DS-06 → "generic"      (mixed anomaly)
  DS-07 → "gps_track"    (latitude/longitude)
  DS-08 → "temperature"  (machine temperature)

For each dataset:
  1. Load all windows (256 samples each)
  2. Encode with mapped preset
  3. Decode
  4. Compute NRMSE per window
  5. Report mean, p95, max NRMSE
  6. FAIL if max NRMSE >= 5% on any window
```

- [x] **Verify:** DT-01 passes on all available datasets.

### Step 1.2: DT-02 — Compression Floor

- [x] **Action:** Create `validation/destruct_tests/dt02_compression_floor.py`.

```
DT-02: Compression Floor
PRD: §5.2, INV-COMPRESSION
PASS CONDITION: CR > 1.0 on EVERY dataset (DS-01..DS-10)
                Mean CR > 5.0 on EVERY dataset (DS-01..DS-08)

For each dataset:
  1. Load all windows
  2. Encode with mapped preset
  3. Compute CR per window
  4. FAIL if ANY window has CR < 1.0
  5. WARN if mean CR < 5.0
```

- [x] **Verify:** DT-02 passes on all available datasets.

### Step 1.3: DT-03 — Determinism (Already Implemented in Phase 1)

- [x] **Action:** Verify DT-03 still passes after Phase 2 code changes.
- [x] **Verify:** 10,000 seeds, bit-identical.

### Step 1.4: DT-04 — Noise Robustness

- [x] **Action:** Create `validation/destruct_tests/dt04_noise_robustness.py`.

```
DT-04: Noise Robustness
PRD: §5.2, INV-FIDELITY
PASS CONDITION: NRMSE < 8% on DS-01..DS-08 with 10dB Gaussian noise added

For each dataset:
  1. Load 100 random windows
  2. Add Gaussian noise at 10dB SNR
  3. Encode noisy signal
  4. Decode
  5. Compute NRMSE (against noisy input, not clean original)
  6. FAIL if mean NRMSE > 8%
```

- [x] **Verify:** DT-04 passes.

### Step 1.5: DT-05 — Pathological Inputs

- [x] **Action:** Create `validation/destruct_tests/dt05_pathological.py`.

```
DT-05: Pathological Inputs
PRD: §5.2, INV-LATCH
PASS CONDITION: No crash, finite output on ALL pathological inputs

Test signals:
  1. All zeros (1000 samples)
  2. All ones (1000 samples)
  3. Single sample (len=1)
  4. Two samples (len=2)
  5. Empty (len=0) — expect graceful error, not crash
  6. NaN-containing signal
  7. Inf-containing signal
  8. Alternating ±1e6
  9. Single impulse (one large value, rest zero)
  10. Step function (0→1 at midpoint)
  11. Maximum float64 values
  12. Extremely small values (1e-300)

For each: encode, decode, verify no crash, no NaN/Inf in output.
```

- [x] **Verify:** DT-05 passes all 12 pathological cases.

### Step 1.6: DT-06 — RAM Budget

- [x] **Action:** Create `validation/destruct_tests/dt06_ram_budget.py`.

```
DT-06: RAM Budget
PRD: §5.2, INV-RAM
PASS CONDITION: Static RAM (.data + .bss) < 4096 bytes on ARM target

Method:
  1. Build: cargo build --release --target thumbv8m.main-none-eabi --no-default-features --features embedded
     (If target not installed, use cargo size on x86 as proxy with explicit budget notation)
  2. Parse: cargo size --release -- -A
  3. Sum .data + .bss sections
  4. FAIL if sum >= 4096
```

- [x] **Verify:** DT-06 passes.

### Step 1.7: DT-07 — Latch Freedom

- [x] **Action:** Create `validation/destruct_tests/dt07_latch_freedom.py`.

```
DT-07: Latch Freedom
PRD: §5.2, INV-LATCH
PASS CONDITION: 10M continuous samples encoded without hang, in < 60 seconds

Method:
  1. Generate 10,000,000 random samples
  2. Encode in 256-sample windows (39,062 windows)
  3. Timeout: 60 seconds total
  4. FAIL if timeout or exception
```

- [x] **Verify:** DT-07 completes within 60 seconds.

---

## Step 2: Implement P1 Destruct Tests

### Step 2.1: DT-08 — DC Torture

- [x] **Action:** Create `validation/destruct_tests/dt08_dc_torture.py`.

```
All-zeros, all-ones, single-value, max-float → No crash, finite output, CR ≥ 1.
```

### Step 2.2: DT-09 — Latency

- [x] **Action:** Create `validation/destruct_tests/dt09_latency.py`.

```
256-sample window, 1000 iterations.
PASS: mean < 0.5ms, p99 < 2ms (host Python; Rust will be faster).
Measure both Python and Rust FFI if available.
```

### Step 2.3: DT-10 — Monotonicity

- [x] **Action:** Create `validation/destruct_tests/dt10_monotonicity.py`.

```
Threshold sweep [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5] on DS-02.
PASS: CR monotonically non-decreasing with threshold.
```

### Step 2.4: DT-11 — Cross-Platform Parity (Verify from Phase 1)

- [x] **Action:** Re-run DT-11 to ensure parity still holds after Phase 2 changes.
- [x] **Verify:** 100 vectors, Python == Rust, bit-identical.

### Step 2.5: DT-12 — Preset Coverage

- [x] **Action:** Create `validation/destruct_tests/dt12_preset_coverage.py`.

```
For each of the 9 presets, encode its target dataset.
PASS: Mean CR >= 5.0 AND mean NRMSE < 5% for each preset.

Preset → Dataset mapping:
  temperature → DS-03
  vibration → DS-02
  accelerometer → DS-04
  pressure → DS-05
  gps_track → DS-07
  voltage → DS-08 (proxy: machine sensor)
  current → DS-08
  flow → DS-03 (proxy: slow-varying)
  generic → DS-06
```

### Step 2.6: DT-13 — Bitpack Integrity (Verify from Phase 1)

- [x] **Action:** Re-run DT-13.
- [x] **Verify:** 10,000 random streams, pack→unpack lossless.

### Step 2.7: DT-14 — CRC Detection

- [x] **Action:** Create `validation/destruct_tests/dt14_crc_detection.py`.

```
1000 valid packed streams.
Corrupt 15%: single-bit (10%), multi-bit (5%).
PASS: CRC detects > 99.9% of corrupted packets.
```

### Step 2.8: DT-15 — Adaptive Stability

- [x] **Action:** Create `validation/destruct_tests/dt15_adaptive_stability.py`.

```
1M continuous samples from DS-02.
Track adaptive threshold over entire stream.
PASS: threshold stays within [THR_MIN=0.001, THR_MAX=1.0] at all times.
No divergence, no NaN, no zero-lock.
```

---

## Step 3: Run Full DT Suite

### Step 3.1: Execute

- [x] **Action:**
```bash
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot"
python validation/destruct_tests/run_all_dts.py
```

- [x] **Verify:** ALL P0 and P1 DTs pass. Document any SKIPPED (dataset unavailable).

### Step 3.2: Pareto Sweep

- [x] **Action:** Run `scripts/pareto_sweep.py` on all available datasets.

For each dataset × threshold combination:
1. Compute mean CR and mean NRMSE
2. Plot Pareto frontier
3. Identify optimal operating point per dataset
4. Check pivot triggers PT-1, PT-2, PT-3

- [x] **Verify:** No pivot trigger fires. Optimal thresholds documented.

### Step 3.3: Establish Baseline

- [x] **Action:** Save current metrics as baseline for DT-16 (regression gate).
```bash
python validation/destruct_tests/run_all_dts.py > /dev/null
cp validation/results/dt_results_*.json validation/results/baseline/
```

- [x] **Verify:** Baseline directory contains timestamped results.

### Step 3.4: Log to CometML

- [x] **Action:** Log all DT results and Pareto sweep to CometML experiment `zpe-iot-phase-2-full-dt-suite`.

---

## Phase 2 Completion Gate

- [x] ALL P0 DTs pass on real datasets (DT-01..DT-07)
- [x] ALL P1 DTs pass (DT-08..DT-15)
- [x] Pareto sweep completed — no pivot triggers
- [x] Baseline established for DT-16
- [x] Results saved to `validation/results/`
- [x] CometML experiments logged
- [x] Phase Gates table in RUNBOOK_00 updated to `PASSED`
- [x] Git commit: `[PHASE-2] Falsification complete, all DTs green`

---

## Addendum A (2026-02-14): Draconian Falsification Upgrade (ACTIVE)

This addendum closes integrity gaps while preserving prior phase history.

### Step A.0: Provenance Schema Upgrade

- [x] **Action:** Extend `validation/datasets/manifest.json` schema to include:
  - `provenance_class` (`proxy`, `real_public`, `real_customer`)
  - `source_url`
  - `license`
  - `retrieval_date_utc`
  - `raw_sha256`
  - `transform_sha256`
  - `notes`
- [x] **Action:** Add `validation/datasets/verify_provenance.py` that validates schema and hash completeness.
- [x] **Verify:** `python validation/datasets/verify_provenance.py` returns exit code 0 only when DS-01..DS-08 meet minimum required fields.

### Step A.1: Mandatory Gate Strictness

- [x] **Action:** Update `validation/destruct_tests/run_all_dts.py`:
  1. Add `--strict-gates` mode.
  2. Treat `SKIPPED` as failure for mandatory DTs in strict mode.
  3. Exit non-zero if any mandatory DT is `SKIPPED`, `FAIL`, `TIMEOUT`, or `NOT_IMPLEMENTED`.
- [x] **Action:** Make strict mode the default for phase-gate runs documented in runbooks.
- [x] **Verify:** Simulated mandatory SKIP causes non-zero process exit and blocks phase pass.

### Step A.2: Eliminate Proxy-PASS in Mandatory DTs

- [x] **Action:** Update DT-06 and DT-16 so missing prerequisites cannot be logged as PASS in gating mode.
- [x] **Action:** If prerequisites are missing, return explicit `SKIPPED` or `FAIL` depending on strict mode contract.
- [x] **Verify:** No code path in mandatory DTs converts missing tooling/data into PASS for gate decisions.

### Step A.3: Evidence Promotion (E0 -> E1)

- [x] **Action:** Replace proxy DS-01..DS-08 assets with real public dataset extracts where licensing allows.
- [x] **Action:** Record retrieval and transformation provenance in manifest fields.
- [x] **Verify:** DS-01..DS-08 are marked `real_public` and pass provenance verification.

### Step A.4: New Hardening DTs

- [x] **Action:** Implement:
  - `dt17_provenance_integrity.py`
  - `dt18_strict_gate_enforcement.py`
  - `dt19_claim_tier_compliance.py`
  - `dt21_architecture_tightness.py`
- [x] **Verify:** DT-17 and DT-18 are mandatory for hardening gate.

### Step A.5: Re-Baseline After Hardening

- [x] **Action:** Run strict full suite and regenerate baseline artifacts:
```bash
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot"
python validation/destruct_tests/run_all_dts.py --strict-gates
```
- [x] **Verify:** Mandatory DTs report PASS with zero SKIP in strict mode.

### Addendum A Completion Gate

- [x] Provenance verifier exists and passes on DS-01..DS-08
- [x] Strict gating is enforced by default in runbook gate commands
- [x] DT-06 and DT-16 cannot PASS via missing-prerequisite fallback in gating context
- [x] Strict full DT run artifact saved and referenced in RUNBOOK_00

---

## Addendum B (2026-02-14B): Falsification Integrity Closure (ACTIVE)

This addendum preserves Addendum A and appends stricter local closure steps.

### Step B.1: Threshold Governance Lock

- [ ] **Action:** Create one source of truth for falsification thresholds:
  - PRD constants/governance values
  - DT implementation constants (`dt04_noise_robustness.py`, `dt12_preset_coverage.py`, related DTs)
- [ ] **Action:** If DT thresholds differ from historical PRD values, append ratification note in PRD with date and rationale.
- [ ] **Verify:** A single audit table maps each threshold to exact file+line and current value.

### Step B.2: Immutable Baseline Contract (DT-16)

- [ ] **Action:** Replace floating "latest baseline file" behavior with pinned baseline identity:
  - `validation/results/baseline/<baseline_tag>/bench_summary.json`
  - `validation/results/baseline/<baseline_tag>/manifest.json` (hashes + creation command + timestamp)
- [ ] **Action:** Update DT-16 to load explicit `baseline_tag` (arg or env) and fail if missing/invalid.
- [ ] **Verify:** Re-running benchmarks cannot silently replace regression reference.

### Step B.3: Draconian Re-Baseline Procedure

- [ ] **Action:** After B.1 and B.2 changes:
```bash
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot"
python validation/destruct_tests/run_all_dts.py --strict-gates
python validation/benchmarks/run_benchmarks.py
python validation/destruct_tests/dt16_benchmark_regression.py --baseline-tag <tag>
```
- [ ] **Verify:** Strict DT summary remains green and DT-16 references pinned baseline tag in output.

### Step B.4: Real-Data Priority Expansion (Local Acquisition Targets)

- [ ] **Action:** Prioritize open, real-public pulls for the 8 presets from these canonical sources:
  - Intel Berkeley Lab (temperature/humidity/voltage),
  - NASA PCoE/PHM turbofan or bearing streams (vibration proxies),
  - Microsoft Geolife trajectories (GPS),
  - NOAA NCEI time-series (environmental pressure/temperature),
  - UCI/Kaggle power and flow datasets where license allows redistribution.
- [ ] **Action:** Record for each source in manifest:
  - URL, license, retrieval date, raw hash, transform hash, preset mapping.
- [ ] **Verify:** New sources are tagged with `real_public` evidence class and pass provenance verifier.

#### B.4 Reference Source Catalog (Seed List)

| Preset(s) | Recommended Source | URL | Notes |
|:---|:---|:---|:---|
| `temperature`, `pressure`, `generic` | NOAA Climate Data Online / NCEI Access | https://www.ncei.noaa.gov/cdo-web/ | Real weather time-series; CDO API token required for web-service API calls. |
| `flow` | USGS Water Data APIs (streamflow) | https://api.waterdata.usgs.gov/ | Real-time and historical flow; public API endpoints available for machine access. |
| `vibration` | CWRU Bearing Data Center | https://engineering.case.edu/bearingdatacenter/welcome | Fault-state vibration traces with documented operating conditions. |
| `vibration`, `accelerometer` | NASA Turbofan degradation (C-MAPSS/PHM08) | https://c3.ndc.nasa.gov/dashlink/resources/139/ | Run-to-failure multichannel sensor streams for stress testing predictive-maintenance presets. |
| `accelerometer` | UCI WISDM Smartphone/Smartwatch | https://archive.ics.uci.edu/ml/datasets/WISDM_Smartphone_and_Smartwatch_Activity_and_Biometrics_Dataset_ | Large raw accelerometer/gyroscope sequence corpus. |
| `voltage`, `current` | UCI Household Electric Power Consumption | https://archive.ics.uci.edu/dataset/235/individual | Minute-level long-span household power stream. |
| `gps_track` | Microsoft Research GeoLife GPS trajectories | https://www.microsoft.com/en-us/research/project/geolife-building-social-networks-using-human-location-history/downloads/ | Longitudinal mobility traces for delta-trajectory compression. |
| `generic`, anomaly stress | Numenta Anomaly Benchmark corpus | https://github.com/numenta/NAB | Mixed real-world streaming telemetry with labels. |
| `flow`, `generic` | UCI Gas sensor dynamic mixtures | https://archive.ics.uci.edu/ml/datasets/Gas%2Bsensor%2Barray%2Bunder%2Bdynamic%2Bgas%2Bmixtures | Long continuous dynamic concentration streams (highly compressible motifs). |

### Step B.5: Access Credential Policy

- [ ] **Action:** Add local env guidance in dataset scripts/docs:
  - `HF_TOKEN` optional for public Hugging Face, required for gated/private
  - `GH_TOKEN` optional for low-volume public fetch, required/recommended for API-heavy or private
  - `KAGGLE_API_TOKEN` supported for Kaggle auth; legacy compatibility path is `KAGGLE_USERNAME` + `KAGGLE_KEY`
- [ ] **Verify:** Download scripts run in no-token mode where possible and fail with explicit remediation when auth is required.

### Addendum B Completion Gate

- [ ] Threshold constants aligned between PRD and DT code
- [ ] DT-16 baseline is immutable and tag-addressed
- [ ] Strict rerun artifact generated after closure changes
- [ ] Expanded real-public dataset mappings documented and hash-verified
- [ ] Credential behavior documented and deterministic

---

**End of RUNBOOK_02. Next: RUNBOOK_03_SDK_PACKAGE.md**

### Addendum B Execution Update (2026-02-14C)

- [x] **Step B.1:** Threshold governance lock
  - Source-of-truth thresholds file: `zpe-iot/validation/destruct_tests/thresholds.py`
  - Audit table with file+line mapping: `zpe-iot/docs/THRESHOLD_GOVERNANCE_AUDIT.md`
  - PRD ratification note appended: `ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md` §16.2.

- [x] **Step B.2:** Immutable baseline contract (DT-16)
  - Pinned baseline tag: `draconian_20260214C`
  - Artifacts:
    - `zpe-iot/validation/results/baseline/draconian_20260214C/bench_summary.json`
    - `zpe-iot/validation/results/baseline/draconian_20260214C/manifest.json`
    - `zpe-iot/validation/results/baseline/ACTIVE_BASELINE_TAG`
  - DT-16 now consumes explicit baseline identity (`--baseline-tag` / env / active tag pointer) and fails on missing/invalid tag.

- [x] **Step B.3:** Draconian re-baseline procedure
  - Strict DT artifact: `zpe-iot/validation/results/dt_results_20260214T202758.json`
  - Benchmark artifact: `zpe-iot/validation/results/bench_summary_20260214T200706.json`
  - DT-16 is green under pinned baseline tag in strict suite.

- [x] **Step B.4:** Real-data priority expansion (local)
  - Provenance verification artifact: strict DT includes `DT-17 PASS`
  - Direct verifier output: `./.venv/bin/python validation/datasets/verify_provenance.py` passed for DS-01..DS-08.
  - Manifest with hash/provenance fields: `zpe-iot/validation/datasets/manifest.json`.

- [x] **Step B.5:** Access credential policy
  - Documented in:
    - `zpe-iot/validation/datasets/README.md`
    - autogenerated README template in `zpe-iot/validation/datasets/download_datasets.py`
  - Script behavior: explicit remediation on 401/403 in `_download` with token guidance (`HF_TOKEN`, `GH_TOKEN`, Kaggle credentials).

### Addendum B Completion Gate Update (2026-02-14C)

- [x] Threshold constants aligned between PRD and DT code
- [x] DT-16 baseline is immutable and tag-addressed
- [x] Strict rerun artifact generated after closure changes
- [x] Expanded real-public dataset mappings documented and hash-verified
- [x] Credential behavior documented and deterministic


### Addendum B Supersession Update (2026-02-14C2)

- `[SUPERSEDED-2026-02-14C2]` Strict rerun artifact reference updated to `zpe-iot/validation/results/dt_results_20260214T205143.json`.
- `[SUPERSEDED-2026-02-14C2]` WI/ZH strict-differential artifacts updated to:
  - `zpe-iot/validation/results/wi1_ablation_20260214T204017.json`
  - `zpe-iot/validation/results/zh1_ablation_20260214T204801.json`

