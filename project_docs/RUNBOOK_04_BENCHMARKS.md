# RUNBOOK_04_BENCHMARKS.md — Phase 4: Public Benchmarks

**STOP.** Have you read `RUNBOOK_00_MASTER.md`? If no, read it NOW.
**Is Phase 3 marked `PASSED` in the Phase Gates table?** If no, go back to `RUNBOOK_03`.

---

## Phase 4 Objective

Run head-to-head benchmarks against industry-standard compressors (zstd, LZ4, zlib, Gorilla). Produce publishable results that prove zpe-iot is superior for sensor time-series data. These benchmarks become the core sales material.

**Input:** Packaged SDK from Phase 3, all DTs green
**Output:** Published benchmark results with charts, `docs/BENCHMARKS.md` filled
**Gating:** PT-6 check (zpe-iot wins > 50% of sensor datasets vs all competitors)
**Duration:** ~10 days

---

## Step 0: Benchmark Infrastructure

### Step 0.1: Create Benchmark Runner

- [x] **Action:** Create `validation/benchmarks/run_benchmarks.py`.

This script:
1. Loads each dataset (DS-01..DS-08)
2. For each dataset, runs: zpe-iot, zstd, LZ4, zlib, Gorilla (where applicable)
3. Measures: CR, NRMSE (for lossy), encode latency, decode latency, peak memory
4. Saves results JSON: `validation/results/bench_<dataset>_<timestamp>.json`
5. Logs to CometML experiment `zpe-iot-phase-4-benchmarks`
6. Prints summary table

**Important:** All compressors get the SAME input — raw float64 bytes. This is the fairest comparison because general compressors can exploit byte-level patterns. If zpe-iot still wins on CR, the argument is strong.

### Step 0.2: Implement Individual Benchmark Scripts

- [x] **Action:** Create the following, each as a standalone comparison:

**`validation/benchmarks/bench_vs_zstd.py`:**
```python
"""Compare zpe-iot vs zstandard (level 3) on all datasets."""
import zstandard as zstd
# For each dataset:
#   raw_bytes = samples.tobytes()
#   zstd_compressed = zstd.ZstdCompressor(level=3).compress(raw_bytes)
#   zstd_cr = len(raw_bytes) / len(zstd_compressed)
#   Compare with zpe-iot CR at same or better NRMSE
```

**`validation/benchmarks/bench_vs_lz4.py`:**
```python
"""Compare zpe-iot vs LZ4 on all datasets."""
import lz4.frame
```

**`validation/benchmarks/bench_vs_zlib.py`:**
```python
"""Compare zpe-iot vs zlib (level 6) on all datasets."""
import zlib
```

**`validation/benchmarks/bench_vs_gorilla.py`:**
```python
"""Compare zpe-iot vs Gorilla (Facebook TSDB compression) on applicable datasets."""
# Gorilla: XOR-based float compression used in time-series databases.
# Implementation: use a reference Python implementation or tsz library.
# If no library available, implement basic Gorilla following the paper.
```

- [x] **Verify:** Each script runs and produces comparison results.

---

## Step 1: Run Full Benchmarks

### Step 1.1: Run All Benchmarks

- [x] **Action:**
```bash
cd "/Users/zer0pa-build/ZPE IoT/zpe-iot"
python validation/benchmarks/run_benchmarks.py
```

### Step 1.2: Collect Results

- [x] **Action:** For each dataset, record:

| Dataset | zpe-iot CR | zpe-iot NRMSE | zstd CR | LZ4 CR | zlib CR | Gorilla CR | Winner |
|:---|:---|:---|:---|:---|:---|:---|:---|
| DS-01 | — | — | — | — | — | — | — |
| DS-02 | — | — | — | — | — | — | — |
| ... | | | | | | | |

### Step 1.3: Check PT-6 (Competitor Parity)

- [x] **Action:** Count how many datasets zpe-iot wins vs each competitor.

```
PT-6 PASS CONDITION: zpe-iot has higher CR than ALL of {zstd, LZ4, zlib}
                     on > 50% of datasets (DS-01..DS-08)
```

If PT-6 fails:
```
1. Identify which datasets zpe-iot loses on
2. Analyse why (high entropy? Low autocorrelation? Uniform distribution?)
3. Tune preset for those signal types
4. Re-run benchmark
5. If still losing after tuning: document limitation honestly
```

- [x] **Verify:** PT-6 passes. Document any datasets where general compressors win.

### Step 1.4: Measure Latency Advantage

- [x] **Action:** For each compressor, measure encode time on 256-sample windows, 1000 iterations.

Expected result: zpe-iot is 10-100x faster than zstd/zlib (because it does domain-specific quantisation, not dictionary search).

Record: mean latency, p99 latency, throughput (samples/sec).

### Step 1.5: Measure Memory Advantage

- [x] **Action:** Measure peak memory usage during encode.

For Python: `tracemalloc.get_traced_memory()`
For Rust: `cargo size --release`

Expected: zpe-iot uses < 4 KB. zstd uses ~128 KB+. LZ4 uses ~16 KB+.

---

## Step 2: Publish Results

### Step 2.1: Generate Charts

- [x] **Action:** Create matplotlib charts:
1. **Bar chart:** CR comparison across all datasets (zpe-iot vs competitors)
2. **Scatter plot:** CR vs NRMSE Pareto frontier for zpe-iot (showing the trade-off)
3. **Bar chart:** Encode latency comparison
4. **Bar chart:** Memory usage comparison
5. **Table:** Complete results matrix

Save charts to `docs/benchmarks/` as PNG.

### Step 2.2: Write BENCHMARKS.md

- [x] **Action:** Fill `docs/BENCHMARKS.md` with:
1. **Methodology** — how benchmarks were run, hardware specs, versions
2. **Results Summary** — headline numbers ("5-10x compression, 100x faster than zstd")
3. **Detailed Results** — per-dataset tables and charts
4. **When NOT to Use ZPE-IoT** — honest limitations (e.g., random data, already compressed)
5. **How to Reproduce** — exact commands to rerun benchmarks

### Step 2.3: Create ROI Calculator

- [x] **Action:** Add to `docs/BENCHMARKS.md` or as standalone script:

```
ROI Calculator:
  Input: number_of_devices, data_rate_bytes_per_day, cellular_cost_per_mb
  Output: annual_cost_before, annual_cost_after, annual_savings, roi_percent

  Example:
    10,000 devices × 1 MB/day × $1.00/MB = $3.65M/year
    At 5x compression: $0.73M/year
    Savings: $2.92M/year
    ZPE-IoT Pro license: $50K/year
    ROI: 58x
```

---

## Step 3: Log and Archive

### Step 3.1: CometML Logging

- [x] **Action:** Log all benchmark results to CometML:
- Experiment: `zpe-iot-phase-4-benchmarks`
- Metrics: CR per dataset per compressor, latency, memory
- Artifacts: result JSONs, charts

### Step 3.2: Archive Results

- [x] **Action:**
```bash
tar czf validation/results/archives/bench_results_$(date +%Y%m%dT%H%M%S).tar.gz \
  validation/results/bench_*.json \
  docs/benchmarks/*.png
```

---

## Phase 4 Completion Gate

- [x] All benchmarks run on available datasets
- [x] PT-6 passes (zpe-iot wins > 50% vs general compressors)
- [x] Charts generated and saved
- [x] `docs/BENCHMARKS.md` complete with methodology, results, and ROI calculator
- [x] Results logged to CometML
- [x] Phase Gates table in RUNBOOK_00 updated to `PASSED`
- [x] Git commit: `[PHASE-4] Benchmarks published, PT-6 green`

---

## Addendum A (2026-02-14): Benchmark Credibility Upgrade (ACTIVE)

This addendum preserves previous outputs and adds stricter benchmark truth controls.

### Step A.1: Evidence-Class Benchmark Split

- [x] **Action:** Produce separate benchmark summaries by evidence class:
  1. `bench_summary_E0_proxy_<timestamp>.json`
  2. `bench_summary_E1_real_public_<timestamp>.json`
  3. `bench_summary_E2_real_customer_<timestamp>.json` (when available)
- [x] **Verify:** `docs/BENCHMARKS.md` clearly labels which summary each claim comes from.

### Step A.2: PT-6 Finalization Rule

- [x] **Action:** Keep current PT-6 as historical `PROVISIONAL` if it used proxy datasets.
- [x] **Action:** Recompute PT-6 on E1 datasets for `FINAL` status.
- [x] **Verify:** `RUNBOOK_00` notes include `PT-6 PROVISIONAL` vs `PT-6 FINAL` state explicitly.

### Step A.3: Reproducibility Envelope

- [x] **Action:** Include the following in benchmark artifacts:
  - dataset manifest hash
  - toolchain versions
  - command lines used
  - hardware profile
- [x] **Verify:** A new engineer can reproduce all published benchmark numbers from docs alone.

### Step A.4: Intersectional Workstream Benchmarking

- [x] **Action:** Benchmark at least one WI candidate (from PRD §14.6) against baseline:
  - control vs candidate
  - CR, NRMSE, latency, RAM
  - ablation across multiple datasets
- [x] **Verify:** Candidate is retained only if gains hold across repeated seeds and no gate regression occurs.

### Addendum A Completion Gate

- [x] E1 benchmark summary generated and published internally
- [x] PT-6 final status computed from E1 or E2 evidence
- [x] Benchmark docs contain explicit evidence-class labels
- [x] Reproducibility metadata included in artifacts

---

## Addendum B (2026-02-14B): Benchmark Truth Closure (ACTIVE)

This addendum is append-only and closes remaining local credibility gaps.

### Step B.1: Evidence Label Rule Enforcement

- [ ] **Action:** Update benchmark summary generation logic so:
  - `FINAL` is legal only when dataset `total > 0` for that evidence tier.
  - `NOT_AVAILABLE` is emitted when `total == 0`.
- [ ] **Action:** Add unit/DT coverage to prevent regression of this label rule.
- [ ] **Verify:** `bench_summary_E2_*` with zero datasets cannot show `FINAL`.

### Step B.2: WI-1 Ablation Fairness Protocol

- [ ] **Action:** Rework WI-1 ablation to use full wire path:
  - packet bytes encode and decode timings,
  - repeated trials (`n >= 5`),
  - per-dataset and aggregate p50/p99 latency.
- [ ] **Action:** Replace static `gate_regression_detected=false` with computed result from strict DT differential.
- [ ] **Verify:** WI retention/removal decision references measured wire-path evidence artifact.

### Step B.3: Headline Claim Synchronization

- [ ] **Action:** Replace generic "5-10x" headlines in README/benchmark docs with:
  - active evidence-tier metric (E1 now),
  - explicit qualifier for dataset class.
- [ ] **Verify:** No top-level claim exceeds active benchmark evidence without qualifier.

### Step B.4: Benchmark Architecture Tightness

- [ ] **Action:** Ensure benchmark and demo scripts avoid asymmetric fast/slow paths between zpe-iot and baselines.
- [ ] **Action:** Emit method metadata in every result artifact:
  - encode/decode pathway,
  - warmup strategy,
  - iteration count,
  - hardware profile.
- [ ] **Verify:** Comparator fairness is auditable from artifact alone.

### Addendum B Completion Gate

- [ ] Evidence label enforcement green in tests and artifacts
- [ ] WI-1 decision based on wire-path repeated-run evidence
- [ ] Public benchmark claims synchronized with current E1/E2 truth
- [ ] Benchmark/demo methodology metadata complete and reproducible

---

**End of RUNBOOK_04. Next: RUNBOOK_05_LAUNCH.md**

### Addendum B Execution Update (2026-02-14C)

- [x] **Step B.1:** Evidence label rule enforcement
  - Implementation: `zpe-iot/validation/benchmarks/run_benchmarks.py`
  - Regression coverage: `zpe-iot/python/tests/test_benchmark_labels.py`, `zpe-iot/validation/destruct_tests/dt19_claim_tier_compliance.py`
  - Verification artifact: `zpe-iot/validation/results/bench_summary_E2_real_customer_20260214T200706.json` (`total=0`, label/status `NOT_AVAILABLE`).

- [x] **Step B.2:** WI-1 ablation fairness protocol
  - Implementation: `zpe-iot/validation/benchmarks/run_wi1_ablation.py`
  - Artifact: `zpe-iot/validation/results/wi1_ablation_20260214T201525.json`
  - Includes wire path, repeats `>=5`, p50/p99 latency, strict-gate differential, and computed `gate_regression_detected`.
  - Decision: WI-1 rejected (default-off) due strict-gate regression.

- [x] **Step B.3:** Headline claim synchronization
  - Updated docs: `zpe-iot/README.md`, `zpe-iot/docs/BENCHMARKS.md`, `zpe-iot/docs/ZPE_IOT_SALES_BRIEF.md`, `zpe-iot/docs/OUTREACH_TEMPLATE.md`.
  - Active claim tier is E1 with explicit metric references.

- [x] **Step B.4:** Benchmark architecture tightness + metadata
  - Fairness updates: `zpe-iot/validation/benchmarks/_common.py`, comparator scripts, `zpe-iot/scripts/customer_demo.py`
  - Method metadata emitted in artifacts, including pathway/warmup/iterations/hardware profile.
  - Verification artifacts:
    - `zpe-iot/validation/results/bench_summary_20260214T200706.json`
    - `zpe-iot/validation/results/customer_demo_20260214T202358.json`

### Addendum B Completion Gate Update (2026-02-14C)

- [x] Evidence label enforcement green in tests and artifacts
- [x] WI-1 decision based on wire-path repeated-run evidence
- [x] Public benchmark claims synchronized with current E1/E2 truth
- [x] Benchmark/demo methodology metadata complete and reproducible


### Addendum B Supersession Update (2026-02-14C2)

- `[SUPERSEDED-2026-02-14C2]` WI-1 evidence artifact now points to `zpe-iot/validation/results/wi1_ablation_20260214T204017.json`.
- `[SUPERSEDED-2026-02-14C2]` Intersectional ZH-1 artifact now points to `zpe-iot/validation/results/zh1_ablation_20260214T204801.json`.

### Addendum B Refresh (2026-02-19E)

- [x] Evidence-label benchmark split regenerated:
  - `zpe-iot/validation/results/bench_summary_E0_proxy_20260219T030604.json`
  - `zpe-iot/validation/results/bench_summary_E1_real_public_20260219T030604.json`
  - `zpe-iot/validation/results/bench_summary_E2_real_customer_20260219T030604.json` (`NOT_AVAILABLE`).
- [x] Wire-path workstream ablation refreshed:
  - WI-1: `zpe-iot/validation/results/wi1_ablation_20260219T025552.json` (rejected, strict-gate regression detected).
  - ZH-1: `zpe-iot/validation/results/zh1_ablation_20260219T030327.json` (rejected, strict-gate regression detected).
- [x] Benchmark table semantics explicitly labeled:
  - `docs/BENCHMARKS.md` now prints `NRMSE(window-normalized)` in result columns.
- [x] PT-6 state remained truthful:
  - E1 FINAL: `PASS (6/8)`.
  - E0 PROVISIONAL: `NOT_AVAILABLE (0/0)`.
  - E2 FINAL: `NOT_AVAILABLE (0/0)`.
