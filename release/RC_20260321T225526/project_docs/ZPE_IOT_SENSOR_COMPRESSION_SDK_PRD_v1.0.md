# ZPE-IoT: 8-Primitive Universal Sensor Compression SDK
## Product Requirements Document & Execution Runbook v1.0

**Codename:** Pulse
**Classification:** Zer0paLab Confidential — MungoDB Poison Pill License
**Date:** 2026-02-13
**Revision:** v1.0 — Initial Commercial SDK Specification
**Status:** RATIFIED — Ready for Phase 0 execution
**Lineage:** Fork from ZPE-Bio Heartbeat codec (Legacy Work). Core 8-primitive algorithm proven in biosignal domain (DT-1..DT-17 green). This PRD generalises the codec for all 1D/2D time-series sensor data.

---

## 0. Why This Exists (Commercial Context)

ZPE-Bio proved the 8-primitive codec works: 5-9x compression, 0.02ms latency, 1KB RAM, deterministic, GPU-free. But the medical market requires FDA 510(k), cardiologist equivalence testing, and 12-18 month regulatory cycles before a single dollar of revenue.

**This PRD pivots the same proven codec to IoT sensor compression** — a market with:
- **Zero regulatory barriers** (no FDA, no clinical validation)
- **Engineer-led purchase cycles** (pip install → benchmark → buy)
- **Pain measured in dollars** (cellular data costs $0.50-$2.00/MB for LTE-M/NB-IoT)
- **Immediate deployment** on existing MCUs (ESP32, STM32, nRF, RISC-V)

**Target:** First paying customer within 60 days of Phase 0 start.

### 0.1 Legacy Provenance

| Asset | Source | Reuse Status |
|:---|:---|:---|
| 8-primitive direction alphabet | ZPE-Bio `codec.py` | **REUSE** (generalise) |
| RLE compression | ZPE-Bio `rle.rs` | **REUSE** (as-is) |
| Log-magnitude table | ZPE-Bio `codec.py` | **REUSE** (as-is) |
| Adaptive threshold envelope | ZPE-Bio `codec.py` | **REUSE** (generalise) |
| Rust `no_std` core | ZPE-Bio `codec.rs` | **REUSE** (refactor quantiser to trait) |
| FFI C bindings | ZPE-Bio `ffi.rs` | **REUSE** (extend) |
| Destruct Test framework | ZPE-Bio `run_all_dts.py` | **REUSE** (adapt datasets) |
| Python test harness | ZPE-Bio `test_codec.py` | **REUSE** (generalise thresholds) |
| ECG-specific quantiser thresholds | ZPE-Bio `quantise.rs` | **DROP** (replace with configurable) |
| MIT-BIH dataset dependency | ZPE-Bio DT-1/DT-2 | **DROP** (replace with IoT datasets) |
| BLE framing (medical GATT) | ZPE-Bio `RUNBOOK_03` | **DROP** (replace with generic transport) |
| FDA/regulatory documentation | ZPE-Bio `RUNBOOK_04` | **DROP** (not applicable) |

---

## 1. Executive Summary

ZPE-IoT is a deterministic, GPU-free, embeddable compression SDK for IoT sensor time-series data. It encodes any 1D signal (temperature, vibration, accelerometer, pressure, GPS trace, current, voltage, flow) as 8-primitive geometric chain codes with optional log-magnitude encoding and hybrid RLE compression. The codec runs on any CPU/MCU — no GPU, no training, no cloud dependency.

### 1.1 Core Objectives

| ID | Objective | Target | Stretch | Measurement |
|:---|:---|:---|:---|:---|
| **OBJ-1** | Compression ratio | CR ≥ 5x | CR ≥ 10x | Mean across benchmark suite |
| **OBJ-2** | Reconstruction fidelity | NRMSE < 5% | NRMSE < 2% | Normalised root-mean-square error |
| **OBJ-3** | Latency | < 0.5ms per 256-sample window | < 0.1ms | Host benchmark (x86/ARM) |
| **OBJ-4** | RAM footprint | < 4 KB static | < 2 KB | `cargo size --release` |
| **OBJ-5** | Binary size | < 16 KB `.text` | < 8 KB | ARM Cortex-M release build |
| **OBJ-6** | Determinism | Bit-identical output | — | 10,000 seed test (DT-3) |
| **OBJ-7** | No external dependencies | Zero runtime deps (no_std) | — | Cargo feature gate audit |
| **OBJ-8** | Time to first paying customer | < 60 days | < 30 days | Revenue event logged |

### 1.2 Product Tiers

| Tier | Name | Target User | Price Model | Content |
|:---|:---|:---|:---|:---|
| **Free** | `zpe-iot-core` | OSS developers, evaluators | MIT license | Rust core + Python bindings, 3 signal presets, CLI tool |
| **Pro** | `zpe-iot-pro` | IoT platform companies | $2-5/device/month or $25K-100K/year site license | All presets, tuning wizard, CometML dashboard, priority support |
| **Embedded** | `zpe-iot-embedded` | MCU OEMs | Per-unit royalty ($0.01-0.05) or flat license | Certified `no_std` library, reference firmware, integration guide |

### 1.3 Non-Goals (Explicit Exclusions)

- **NOT** a general-purpose compression algorithm (not competing with zstd/LZ4 on arbitrary data)
- **NOT** doing lossy image/audio compression
- **NOT** doing ML inference or model training
- **NOT** building a cloud platform or SaaS dashboard (that's a future play)
- **NOT** pursuing FDA/CE certification in this PRD cycle
- **NOT** building custom hardware

---

## 2. Technical Specification

### 2.1 Geometric Primitives (Inherited from ZPE-Bio)

The codec uses a 3-bit directional alphabet (0-7) representing discrete trajectory directions:

| Code | Direction | Delta Sign | Magnitude Band |
|:---|:---|:---|:---|
| `0` | FLAT | 0 | Below threshold (no change) |
| `1` | RISE_GENTLE | + | 1x-4x threshold |
| `2` | RISE_MODERATE | + | 4x-16x threshold |
| `3` | RISE_STEEP | + | 16x-64x threshold |
| `4` | RISE_EXTREME | + | >64x threshold |
| `5` | FALL_EXTREME | - | >64x threshold |
| `6` | FALL_MODERATE | - | 4x-64x threshold |
| `7` | FALL_GENTLE | - | 1x-4x threshold |

**Design rationale:** 3 bits = 8 states. This is the minimum sufficient representation for directional change in a 1D signal while preserving monotonic magnitude ordering. The alphabet is symmetric: 1 flat + 4 rise + 3 fall (FLAT absorbs the 8th state for RLE efficiency on stable signals, which dominate IoT sensor data).

### 2.2 Encoding Modes

| Mode | Bit Budget/Token | Fields | Use Case | Expected CR |
|:---|:---|:---|:---|:---|
| **FAST** | 3 bits | Direction only | Maximum compression, lossy | 8-15x |
| **BALANCED** | 9 bits | Direction (3) + Magnitude (6) | Good fidelity, good compression | 5-10x |
| **LOSSLESS_DELTA** | Variable | Direction (3) + Residual (variable) | Exact reconstruction of quantised delta | 3-6x |

### 2.3 Encoding Pipeline

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Raw Samples │───▶│  Delta       │───▶│  Quantise    │───▶│  RLE         │───▶│  Bit-Pack    │
│  f64[] / i16 │    │  Extraction  │    │  to 8-Dir +  │    │  Compress    │    │  to Bytes    │
│              │    │  Δ[i]=x[i]-  │    │  Opt. Mag    │    │  (d,m,count) │    │  Output      │
│              │    │     x̂[i-1]   │    │              │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                                       │
                         ┌─────────────────────────────────────────────────────────────┘
                         ▼
                    ┌──────────────┐
                    │  Compressed  │
                    │  Byte Stream │
                    │  + Metadata  │
                    └──────────────┘
```

### 2.4 Quantisation Algorithm (Generalised)

```python
def quantise_delta(delta: float, threshold: float, bands: list[float]) -> int:
    """
    Map a sample-to-sample delta to one of 8 directions.

    bands: list of 3 positive thresholds [gentle, moderate, steep]
           default = [1.0, 4.0, 16.0] (multiplied by threshold)

    Returns direction code 0-7.
    """
    abs_d = abs(delta)
    if abs_d < threshold:
        return 0  # FLAT
    sign = 1 if delta > 0 else -1

    if abs_d < bands[0] * threshold:
        level = 1  # GENTLE
    elif abs_d < bands[1] * threshold:
        level = 2  # MODERATE
    elif abs_d < bands[2] * threshold:
        level = 3  # STEEP
    else:
        level = 4  # EXTREME

    if sign > 0:
        return level        # 1, 2, 3, 4
    else:
        return 8 - level    # 7, 6, 5, 4  (symmetric mapping)
```

**Key difference from ZPE-Bio:** The `bands` parameter is now configurable per signal type, not hardcoded. This is the critical generalisation.

### 2.5 Log-Magnitude Table (Inherited)

For BALANCED mode, magnitudes are quantised to a 64-entry Weber-Fechner logarithmic table:

```
LOG_MAG_TABLE[i] = round(LOG_BASE ^ i)    where LOG_BASE = 1.091928, i ∈ [0, 63]
```

This gives constant *relative* error across 6 orders of magnitude — critical for sensor data where signal amplitude varies widely (e.g., vibration: micro-g to multi-g).

### 2.6 Adaptive Threshold (Inherited + Extended)

The codec tracks signal energy with an exponential envelope follower:

```
envelope[i] = max(ALPHA * envelope[i-1], |delta[i]|)
threshold[i] = max(K * envelope[i], THR_MIN)
```

**Extension for IoT:** Add `THR_MAX` ceiling to prevent threshold runaway on sensor spikes (e.g., impact events in accelerometer data). ZPE-Bio did not need this because ECG amplitude is bounded.

### 2.7 Signal Presets (New)

Pre-tuned configurations for common IoT sensor types. Users can override any parameter.

| Preset | Sample Rate | Threshold | Step | Bands | Mode | Expected CR |
|:---|:---|:---|:---|:---|:---|:---|
| `temperature` | 1-10 Hz | 0.05 | 0.1 | [1, 2, 4] | FAST | 10-30x |
| `vibration` | 1-25 kHz | 0.02 | 0.01 | [1, 4, 16] | BALANCED | 5-10x |
| `accelerometer` | 50-400 Hz | 0.03 | 0.01 | [1, 4, 16] | BALANCED | 5-12x |
| `pressure` | 1-100 Hz | 0.01 | 0.1 | [1, 2, 8] | BALANCED | 8-20x |
| `gps_track` | 1-10 Hz | 0.001 | 0.0001 | [1, 4, 16] | BALANCED | 5-15x |
| `voltage` | 50-10k Hz | 0.02 | 0.01 | [1, 4, 16] | BALANCED | 5-10x |
| `current` | 50-10k Hz | 0.02 | 0.01 | [1, 4, 16] | BALANCED | 5-10x |
| `flow` | 1-100 Hz | 0.03 | 0.1 | [1, 2, 8] | FAST | 8-20x |
| `generic` | any | 0.05 | auto | [1, 4, 16] | BALANCED | 5-10x |

**Auto-step:** When `step=auto`, the codec computes `step = std(samples) / 64` on the first window. This is a one-time calibration cost.

### 2.8 Bit-Packing Format

```
┌─────────────────────────────────────────────────┐
│ HEADER (4 bytes)                                │
│   magic:     0x5A50 ("ZP")            [2 bytes] │
│   version:   0x01                     [1 byte]  │
│   flags:     mode(2) | preset(4) |   [1 byte]  │
│              adaptive(1) | reserved(1)          │
├─────────────────────────────────────────────────┤
│ METADATA (8 bytes)                              │
│   sample_count:   u16                 [2 bytes] │
│   start_value:    f32                 [4 bytes] │
│   step:           f16                 [2 bytes] │
├─────────────────────────────────────────────────┤
│ PAYLOAD (variable)                              │
│   Packed RLE tokens:                            │
│     FAST mode:                                  │
│       direction(3 bits) + count(5 bits)         │
│       = 1 byte per RLE token                    │
│     BALANCED mode:                              │
│       direction(3) + magnitude(6) + count(7)    │
│       = 2 bytes per RLE token                   │
├─────────────────────────────────────────────────┤
│ CRC-16-CCITT (2 bytes)                          │
└─────────────────────────────────────────────────┘
```

Total overhead: 14 bytes fixed. For a 256-sample window at 5x compression, payload ≈ 100 bytes → total ≈ 114 bytes.

---

## 3. SDK Architecture

### 3.1 Project Layout

```
/Users/zer0pa-build/ZPE IoT/                        ← PROJECT ROOT
├── ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md        ← THIS FILE (source of truth)
├── RUNBOOK_00_MASTER.md                               ← Master orchestration
├── RUNBOOK_01_CORE_CODEC.md                           ← Phase 1: Core codec
├── RUNBOOK_02_FALSIFICATION.md                        ← Phase 2: Destruct tests
├── RUNBOOK_03_SDK_PACKAGE.md                          ← Phase 3: SDK packaging
├── RUNBOOK_04_BENCHMARKS.md                           ← Phase 4: Public benchmarks
├── RUNBOOK_05_LAUNCH.md                               ← Phase 5: Ship & sell
├── Legacy Work/                                       ← Previous ZPE-Bio work (read-only reference)
└── zpe-iot/                                           ← CODE REPOSITORY
    ├── core/                                          ← Rust codec (canonical implementation)
    │   ├── src/
    │   │   ├── lib.rs                                 ← Public API surface
    │   │   ├── codec.rs                               ← Encode/decode logic
    │   │   ├── quantise.rs                            ← 8-direction quantiser (trait-based)
    │   │   ├── rle.rs                                 ← Run-length encoding
    │   │   ├── magnitude.rs                           ← Log-magnitude table + lookup
    │   │   ├── adaptive.rs                            ← Adaptive threshold envelope
    │   │   ├── bitpack.rs                             ← Bit-packing + CRC
    │   │   ├── presets.rs                             ← Signal type presets
    │   │   └── ffi.rs                                 ← C FFI exports
    │   ├── tests/
    │   │   ├── test_codec.rs                          ← Property-based tests (proptest)
    │   │   └── test_parity.rs                         ← Cross-platform parity
    │   ├── Cargo.toml
    │   └── cbindgen.toml                              ← C header generation config
    ├── python/                                        ← Python SDK (reference + bindings)
    │   ├── zpe_iot/
    │   │   ├── __init__.py
    │   │   ├── codec.py                               ← Pure-Python reference implementation
    │   │   ├── presets.py                             ← Signal presets
    │   │   ├── _native.py                             ← Rust FFI bindings (cffi/PyO3)
    │   │   └── cli.py                                 ← CLI entry point
    │   ├── tests/
    │   │   ├── test_codec.py                          ← Unit + property tests
    │   │   ├── test_parity.py                         ← Python-Rust parity
    │   │   └── test_presets.py                        ← Preset validation
    │   └── pyproject.toml
    ├── c/                                             ← C header + example
    │   ├── zpe_iot.h                                  ← Generated header (cbindgen)
    │   └── example.c                                  ← Minimal usage example
    ├── validation/                                    ← Falsification harness
    │   ├── destruct_tests/
    │   │   ├── run_all_dts.py                         ← Master DT runner
    │   │   ├── dt01_fidelity.py                       ← NRMSE < 5% on all benchmark signals
    │   │   ├── dt02_compression_floor.py              ← CR > 1.0 on all signals (no expansion)
    │   │   ├── dt03_determinism.py                    ← Bit-identical over 10,000 seeds
    │   │   ├── dt04_noise_robustness.py               ← NRMSE < 8% under 10dB SNR
    │   │   ├── dt05_pathological.py                   ← No crash on DC, impulse, NaN, Inf, empty
    │   │   ├── dt06_ram_budget.py                     ← Static RAM < 4 KB
    │   │   ├── dt07_latch_freedom.py                  ← 10M-sample stream, no hang
    │   │   ├── dt08_dc_torture.py                     ← Flat signal produces finite output
    │   │   ├── dt09_latency.py                        ← Encode < 0.5ms per 256-sample window
    │   │   ├── dt10_monotonicity.py                   ← CR increases monotonically with threshold
    │   │   ├── dt11_cross_platform.py                 ← Python-Rust bit-identical output
    │   │   ├── dt12_preset_coverage.py                ← All presets pass OBJ-1 and OBJ-2
    │   │   ├── dt13_bitpack_integrity.py              ← Pack → unpack round-trip lossless
    │   │   ├── dt14_crc_detection.py                  ← >99.9% corruption detection on 1000 packets
    │   │   ├── dt15_adaptive_stability.py             ← Adaptive threshold does not diverge over 1M samples
    │   │   └── dt16_benchmark_regression.py           ← No metric regression vs baseline
    │   ├── benchmarks/
    │   │   ├── run_benchmarks.py                      ← Comparative benchmark runner
    │   │   ├── bench_vs_zstd.py                       ← Comparison: zpe-iot vs zstd on sensor data
    │   │   ├── bench_vs_lz4.py                        ← Comparison: zpe-iot vs LZ4
    │   │   ├── bench_vs_zlib.py                       ← Comparison: zpe-iot vs zlib
    │   │   └── bench_vs_gorilla.py                    ← Comparison: zpe-iot vs Gorilla (Facebook TSDB)
    │   ├── datasets/                                  ← Public benchmark datasets
    │   │   ├── README.md                              ← Dataset provenance documentation
    │   │   └── download_datasets.py                   ← Automated dataset fetcher
    │   └── results/                                   ← Timestamped JSON results
    ├── examples/                                      ← Usage examples
    │   ├── python/
    │   │   ├── quickstart.py                          ← 10-line encode/decode
    │   │   ├── csv_compressor.py                      ← Compress CSV sensor logs
    │   │   └── mqtt_bridge.py                         ← MQTT publish with compression
    │   ├── rust/
    │   │   └── embedded_demo/                         ← Cortex-M example project
    │   └── c/
    │       └── arduino_demo/                          ← Arduino/PlatformIO example
    ├── scripts/
    │   ├── pareto_sweep.py                            ← Threshold sweep for optimal CR/fidelity
    │   ├── tuning_wizard.py                           ← Interactive preset tuner for new signal types
    │   └── generate_c_header.sh                       ← cbindgen wrapper
    └── docs/
        ├── API.md                                     ← SDK API reference
        ├── BENCHMARKS.md                              ← Published benchmark results
        ├── INTEGRATION_GUIDE.md                       ← How to integrate into your project
        ├── SESSION_LOG.md                              ← Agent session history
        └── CHANGELOG.md                               ← Version history
```

### 3.2 Dependency Inventory

**Rust Core (production — zero external deps in no_std mode):**

| Crate | Version | Feature | Purpose |
|:---|:---|:---|:---|
| `heapless` | 0.8 | — | Fixed-capacity collections for no_std |
| (none others in `no_std` mode) | — | — | — |

**Rust Core (dev/test only):**

| Crate | Version | Purpose |
|:---|:---|:---|
| `proptest` | 1.4 | Property-based testing |

**Python SDK:**

| Package | Version | Purpose |
|:---|:---|:---|
| `numpy` | >=1.24 | Array operations |
| `cffi` | >=1.16 | Rust FFI bindings |
| `click` | >=8.0 | CLI interface |

**Python Dev/Test:**

| Package | Version | Purpose |
|:---|:---|:---|
| `pytest` | >=7.0 | Test framework |
| `hypothesis` | >=6.0 | Property-based testing |
| `comet_ml` | >=3.35 | Experiment tracking |
| `zstandard` | >=0.22 | Benchmark comparison |
| `lz4` | >=4.3 | Benchmark comparison |
| `matplotlib` | >=3.7 | Visualisation (optional) |

### 3.3 Public API Surface

**Python:**

```python
import zpe_iot

# Encode with preset
compressed = zpe_iot.encode(samples, preset="vibration")

# Encode with custom config
compressed = zpe_iot.encode(
    samples,
    mode="balanced",
    threshold=0.02,
    step=0.01,
    bands=[1, 4, 16],
    adaptive=True,
)

# Decode
reconstructed = zpe_iot.decode(compressed)

# Metrics
cr = compressed.compression_ratio      # float
nrmse = compressed.nrmse(samples)      # float (0-1)
size_bytes = compressed.packed_size     # int

# CLI
# $ zpe-iot compress sensor_data.csv --preset vibration --output compressed.zpk
# $ zpe-iot decompress compressed.zpk --output restored.csv
# $ zpe-iot benchmark sensor_data.csv --compare zstd,lz4,zlib
```

**Rust:**

```rust
use zpe_iot::{encode, decode, Preset, Config, Mode};

// With preset
let compressed = encode::<1024>(&samples, &Preset::Vibration.config())?;

// With custom config
let cfg = Config {
    mode: Mode::Balanced,
    threshold: 0.02,
    step: 0.01,
    bands: [1.0, 4.0, 16.0],
    adaptive: true,
    ..Default::default()
};
let compressed = encode::<1024>(&samples, &cfg)?;

// Decode
let mut output = [0.0f64; 1024];
let n = decode(&compressed, &mut output)?;
```

**C:**

```c
#include "zpe_iot.h"

zpe_iot_config_t cfg = zpe_iot_preset_vibration();
zpe_iot_result_t result;
int32_t status = zpe_iot_encode(samples, n_samples, &cfg, &result);

float cr = zpe_iot_compression_ratio(&result);
int32_t n_decoded = zpe_iot_decode(&result, output_buf, output_buf_len);
```

---

## 4. Benchmark Datasets (Replacing MIT-BIH)

### 4.1 Primary Benchmark Suite

All datasets must be publicly available, freely downloadable, and cited in published work.

| ID | Dataset | Signal Type | Source | Samples | Sample Rate | Notes |
|:---|:---|:---|:---|:---|:---|:---|
| **DS-01** | UCI Gas Sensor Array | Chemical | UCI ML Repository | 4M+ | 100 Hz | 16 sensors, drift detection |
| **DS-02** | FEMTO Bearing Vibration | Vibration | NASA Prognostics | 2.5M | 25.6 kHz | Accelerometer, run-to-failure |
| **DS-03** | Intel Lab Temperature | Temperature | UCI ML Repository | 2.3M | 0.03 Hz (31s) | 54 sensors, 2 months |
| **DS-04** | SHL Locomotion IMU | Accelerometer | Sussex-Huawei | 20M+ | 100 Hz | 3-axis accelerometer |
| **DS-05** | NOAA Weather (hourly) | Multi (temp, pressure, wind) | NOAA ISD | 100M+ | 1/3600 Hz | Global stations |
| **DS-06** | Numenta NAB | Anomaly (mixed) | Numenta Benchmark | 365K | Various | 58 time series, diverse |
| **DS-07** | GeoLife GPS Trajectories | GPS | Microsoft Research | 25M+ | 1-5 Hz | 182 users, 5 years |
| **DS-08** | DEBS 2012 Manufacturing | Machine sensor | ACM DEBS | 10M+ | Various | Temperature + power |
| **DS-09** | Synthetic White Noise | Noise baseline | Generated | 1M | 1000 Hz | Codec lower bound |
| **DS-10** | Synthetic Sine Sweep | Baseline | Generated | 1M | 1000 Hz | Codec upper bound |

### 4.2 Benchmark Protocol

Every benchmark run MUST:
1. Use the exact dataset version pinned in `validation/datasets/README.md`
2. Report: CR, NRMSE, encode latency (mean, p50, p99), decode latency, peak RAM
3. Compare against: raw, zstd -3, LZ4, zlib -6, Gorilla (where applicable)
4. Log all results to CometML experiment `zpe-iot-phase-N-<description>`
5. Save JSON results to `validation/results/bench_<dataset>_<timestamp>.json`

### 4.3 Comparison Methodology

All comparisons are **apples-to-apples**: same input data, same machine, same measurement protocol.

For general-purpose compressors (zstd, LZ4, zlib):
- Input: raw bytes of the float64 samples (to give them the best case)
- No domain-specific preprocessing applied to the competitor

For domain-specific compressors (Gorilla):
- Input: timestamped samples in their native format
- Use default/recommended settings

---

## 5. Falsification Protocol (The Hound of Popper)

### 5.1 Invariants

| ID | Invariant | Description | Test |
|:---|:---|:---|:---|
| **INV-DET** | Determinism | `encode(x) == encode(x)` always | DT-03 |
| **INV-FIDELITY** | Fidelity floor | NRMSE < 5% on all benchmark signals in BALANCED mode | DT-01 |
| **INV-COMPRESSION** | Compression floor | CR > 1.0 on all inputs (never expand) | DT-02 |
| **INV-RAM** | Memory bound | Static allocation < 4 KB | DT-06 |
| **INV-LATCH** | Latch freedom | No hang/deadlock on any input, including adversarial | DT-07 |
| **INV-PACK** | Pack integrity | `unpack(pack(x)) == x` bit-identical | DT-13 |

### 5.2 Destruct Tests

| DT | Name | Invariant | Input | Pass Condition | Priority |
|:---|:---|:---|:---|:---|:---|
| **DT-01** | Fidelity Gate | INV-FIDELITY | All DS-01..DS-08 | NRMSE < 5% on EVERY dataset (BALANCED mode) | **P0** |
| **DT-02** | Compression Floor | INV-COMPRESSION | All DS-01..DS-10 | CR > 1.0 on EVERY dataset | **P0** |
| **DT-03** | Determinism | INV-DET | 10,000 random seeds | Bit-identical output for same input | **P0** |
| **DT-04** | Noise Robustness | INV-FIDELITY | DS-01..DS-08 + 10dB Gaussian noise | NRMSE < 8% | **P0** |
| **DT-05** | Pathological Inputs | INV-LATCH | DC, impulse, NaN, Inf, empty, len=1, alternating extremes | No crash, finite output | **P0** |
| **DT-06** | RAM Budget | INV-RAM | `cargo size --release` on ARM target | `.data + .bss < 4096` bytes | **P0** |
| **DT-07** | Latch Freedom | INV-LATCH | 10M continuous samples | No hang, completes in < 60s | **P0** |
| **DT-08** | DC Torture | INV-DET | All-zeros, all-ones, single-value, max-float | No crash, finite output, CR ≥ 1 | **P1** |
| **DT-09** | Latency | — | 256-sample window, 1000 iterations | Mean < 0.5ms, p99 < 2ms (host) | **P1** |
| **DT-10** | Monotonicity | — | Threshold sweep [0.001..0.5] on DS-02 | CR monotonically non-decreasing | **P1** |
| **DT-11** | Cross-Platform Parity | INV-DET | 100 test vectors | Python output == Rust output, byte-identical | **P1** |
| **DT-12** | Preset Coverage | INV-FIDELITY, INV-COMPRESSION | Each preset on its target dataset | OBJ-1 AND OBJ-2 met | **P1** |
| **DT-13** | Bitpack Integrity | INV-PACK | 10,000 random encoded streams | `unpack(pack(x)) == x` | **P1** |
| **DT-14** | CRC Detection | — | 1000 packets, 15% corruption | Detection rate > 99.9% | **P1** |
| **DT-15** | Adaptive Stability | — | 1M continuous samples from DS-02 | Threshold stays within [THR_MIN, THR_MAX] | **P1** |
| **DT-16** | Benchmark Regression | — | Full benchmark suite vs saved baseline | No metric degrades > 5% from baseline | **P2** |

### 5.3 Pivot Triggers

| ID | Trigger | Condition | Action |
|:---|:---|:---|:---|
| **PT-1** | Compression Miss | Mean CR < 3x on > 3 datasets | Architecture review: evaluate entropy coding stage |
| **PT-2** | Fidelity Miss | Mean NRMSE > 8% on > 3 datasets in BALANCED | Architecture review: evaluate higher-bit magnitude |
| **PT-3** | Joint Miss | PT-1 AND PT-2 fire simultaneously | **ARCHITECTURE_BREAK**: freeze feature work, execute Pareto rescue |
| **PT-4** | Latency Miss | Mean encode > 2ms | Profile: hot-path optimisation |
| **PT-5** | RAM Miss | Static > 8 KB | Profile: buffer sizing audit |
| **PT-6** | Competitor Parity | zstd beats zpe-iot on > 50% of datasets at same fidelity | Re-evaluate value proposition |

### 5.4 CometML Logging Protocol

Every DT run and benchmark MUST log to CometML:

```python
import comet_ml

experiment = comet_ml.Experiment(
    project_name="zpe-iot",
    workspace="zer0pa",
    auto_metric_logging=False,
)
experiment.set_name(f"dt-{dt_number:02d}-{datetime.now().strftime('%Y%m%dT%H%M%S')}")
experiment.add_tag(f"phase-{phase}")
experiment.add_tag(f"priority-{priority}")

# Log metrics
experiment.log_metric("compression_ratio_mean", cr_mean)
experiment.log_metric("nrmse_mean", nrmse_mean)
experiment.log_metric("latency_mean_ms", latency_mean)
experiment.log_metric("ram_bytes", ram_bytes)
experiment.log_metric("dt_pass", 1 if passed else 0)

# Log dataset used
experiment.log_parameter("dataset", dataset_name)
experiment.log_parameter("preset", preset_name)
experiment.log_parameter("mode", mode)

# Log result artifact
experiment.log_asset(result_json_path)
```

**If CometML is unavailable** (no API key, offline): fall back to `docs/SESSION_LOG.md` with the same metrics in markdown table format. The DT runner MUST NOT fail because CometML is unreachable.

---

## 6. Exact Constants & Thresholds

**These are NOT configurable without PRD amendment.** Changing any value requires PRD update + full DT re-run.

| Constant | Value | Unit | Used In |
|:---|:---|:---|:---|
| `DIRECTION_COUNT` | 8 | — | Quantiser (3-bit alphabet) |
| `LOG_BASE` | 1.091928 | scalar | Magnitude table generation |
| `LOG_MAG_TABLE_SIZE` | 64 | entries | Magnitude lookup (6-bit index) |
| `ADAPTIVE_K` | 0.15 | scalar | Threshold envelope multiplier |
| `ADAPTIVE_THR_MIN` | 0.001 | normalised | Threshold floor |
| `ADAPTIVE_THR_MAX` | 1.0 | normalised | Threshold ceiling (NEW) |
| `ADAPTIVE_ALPHA` | 0.95 | scalar | Envelope decay factor |
| `DEFAULT_WINDOW_SIZE` | 256 | samples | Encode window size |
| `MAX_RLE_COUNT` | 65535 | u16 max | RLE run-length limit |
| `MAX_RAM_BYTES` | 4096 | bytes | Embedded RAM budget |
| `MAX_STACK_BYTES` | 4096 | bytes | Embedded stack budget |
| `PACKET_MAGIC` | 0x5A50 | u16 | Packet sync marker ("ZP") |
| `PACKET_VERSION` | 0x01 | u8 | Wire format version |
| `CRC_POLY` | 0x1021 | — | CRC-16-CCITT polynomial |
| `TARGET_CR` | 5.0 | ratio | Compression ratio target |
| `STRETCH_CR` | 10.0 | ratio | Compression ratio stretch |
| `MAX_NRMSE` | 0.05 | fraction | Maximum normalised RMSE (5%) |
| `MAX_NRMSE_NOISY` | 0.08 | fraction | Max NRMSE under noise (8%) |
| `DEFAULT_BANDS` | [1.0, 4.0, 16.0] | [float; 3] | Default quantisation band multipliers |
| `BENCHMARK_DATASETS` | 10 | count | DS-01..DS-10 |

---

## 7. Execution Runbook

### Phase 0: Repository Setup (Day 1)

| Step | Action | Gating | Verify |
|:---|:---|:---|:---|
| 0.1 | Create `zpe-iot/` directory structure per §3.1 | — | `find . -type d \| sort` matches layout |
| 0.2 | Create `core/Cargo.toml` with deps from §3.2 | — | `cargo check` passes |
| 0.3 | Create `python/pyproject.toml` with deps from §3.2 | — | `pip install -e .` passes |
| 0.4 | Create DT script stubs (dt01..dt16) | — | All 16 files exist |
| 0.5 | Create `run_all_dts.py` master runner | — | `python run_all_dts.py` runs (all NOT_IMPLEMENTED) |
| 0.6 | Copy and generalise `rle.rs` from Legacy | — | `cargo test` passes |
| 0.7 | Initialise git repo, initial commit | — | `git log` shows commit |
| 0.8 | Log Phase 0 to CometML or SESSION_LOG.md | — | Entry exists |

### Phase 1: Core Codec (Days 2-10)

| Step | Action | Gating DTs | Verify |
|:---|:---|:---|:---|
| 1.1 | Implement `quantise.rs` with trait-based quantiser | — | Unit tests pass |
| 1.2 | Implement `magnitude.rs` (LOG_MAG_TABLE) | — | Table generation matches formula |
| 1.3 | Implement `adaptive.rs` (threshold envelope) | — | Envelope tracks correctly on synthetic |
| 1.4 | Implement `codec.rs` (encode + decode, FAST mode) | DT-03 | Determinism passes |
| 1.5 | Implement `codec.rs` (BALANCED mode) | DT-01, DT-02 | Fidelity + compression floor on DS-09/DS-10 |
| 1.6 | Implement `bitpack.rs` (pack/unpack + CRC) | DT-13 | Round-trip lossless |
| 1.7 | Implement `presets.rs` (all 9 presets from §2.7) | — | All presets instantiate without panic |
| 1.8 | Port codec to Python (`codec.py`) | — | Python unit tests pass |
| 1.9 | Build FFI (`ffi.rs`) + Python bindings (`_native.py`) | DT-11 | Python-Rust parity on 100 vectors |
| 1.10 | Implement CLI (`cli.py`) | — | `zpe-iot compress` and `zpe-iot decompress` work |
| 1.11 | Run all P0 DTs | DT-01..DT-07 | ALL P0 pass |
| 1.12 | Log Phase 1 to CometML | — | Experiment logged |

**Phase 1 Gate:** ALL P0 DTs pass. If ANY P0 fails, do NOT proceed.

### Phase 2: Falsification (Days 11-18)

| Step | Action | Gating DTs | Verify |
|:---|:---|:---|:---|
| 2.1 | Download all benchmark datasets (DS-01..DS-10) | — | `download_datasets.py` completes |
| 2.2 | Implement DT-01 on full dataset suite | DT-01 | NRMSE < 5% on all |
| 2.3 | Implement DT-02 on full dataset suite | DT-02 | CR > 1.0 on all |
| 2.4 | Implement DT-04 (noise robustness) | DT-04 | NRMSE < 8% under noise |
| 2.5 | Implement DT-08..DT-10 (P1 tests) | DT-08..DT-10 | All pass |
| 2.6 | Implement DT-12 (preset coverage) | DT-12 | All presets meet targets |
| 2.7 | Implement DT-14..DT-15 (CRC + adaptive stability) | DT-14, DT-15 | All pass |
| 2.8 | Run full DT suite (`run_all_dts.py`) | ALL | All P0+P1 pass |
| 2.9 | Run Pareto sweep (`pareto_sweep.py`) | — | Optimal thresholds documented per dataset |
| 2.10 | Save baseline metrics for DT-16 regression gate | DT-16 | Baseline JSON created |
| 2.11 | Log Phase 2 to CometML | — | All DT experiments logged |

**Phase 2 Gate:** ALL P0+P1 DTs pass. DT-16 baseline established.

### Phase 3: SDK Packaging (Days 19-30)

| Step | Action | Gating | Verify |
|:---|:---|:---|:---|
| 3.1 | Write `API.md` documentation | — | All public API documented |
| 3.2 | Write `INTEGRATION_GUIDE.md` | — | Step-by-step for Python, Rust, C |
| 3.3 | Create `examples/python/quickstart.py` | — | Runs in < 10 lines |
| 3.4 | Create `examples/python/csv_compressor.py` | — | Compresses real CSV |
| 3.5 | Create `examples/rust/embedded_demo/` | — | Compiles for thumbv7em |
| 3.6 | Create `examples/c/arduino_demo/` | — | Compiles with PlatformIO |
| 3.7 | Generate C header (`zpe_iot.h`) via cbindgen | — | Header compiles with gcc |
| 3.8 | Build Python wheel (`pip install .`) | — | `import zpe_iot; zpe_iot.encode(...)` works |
| 3.9 | Publish to TestPyPI | — | `pip install -i test.pypi.org zpe-iot` works |
| 3.10 | Create GitHub repo with README, LICENSE (MIT) | — | Repo accessible |
| 3.11 | Log Phase 3 to CometML | — | Package artifacts logged |

**Phase 3 Gate:** SDK installable via pip. All examples run. Documentation complete.

### Phase 4: Public Benchmarks (Days 31-40)

| Step | Action | Gating | Verify |
|:---|:---|:---|:---|
| 4.1 | Run `bench_vs_zstd.py` on all datasets | — | Results JSON saved |
| 4.2 | Run `bench_vs_lz4.py` on all datasets | — | Results JSON saved |
| 4.3 | Run `bench_vs_zlib.py` on all datasets | — | Results JSON saved |
| 4.4 | Run `bench_vs_gorilla.py` on applicable datasets | — | Results JSON saved |
| 4.5 | Generate `BENCHMARKS.md` with tables and charts | — | Published to repo |
| 4.6 | Verify PT-6 (competitor parity) | PT-6 | zpe-iot wins > 50% of sensor datasets |
| 4.7 | Log Phase 4 to CometML | — | All benchmark experiments logged |

**Phase 4 Gate:** Benchmarks published. zpe-iot demonstrably superior to general compressors on sensor data.

### Phase 5: Launch & Sell (Days 41-60)

| Step | Action | Gating | Verify |
|:---|:---|:---|:---|
| 5.1 | Publish to PyPI (`pip install zpe-iot`) | — | Install works globally |
| 5.2 | Publish to crates.io (`cargo add zpe-iot`) | — | Build works |
| 5.3 | Write launch blog post / HN post | — | Published |
| 5.4 | Create landing page with benchmark charts | — | URL live |
| 5.5 | Identify 10 IoT companies with cellular data costs | — | List of 10 with contacts |
| 5.6 | Send cold outreach with benchmark results | — | 10 emails sent |
| 5.7 | Offer free pilot (compress their data, show savings) | — | 3 pilots started |
| 5.8 | Close first paying customer | — | **Revenue event** |
| 5.9 | Log Phase 5 to CometML | — | Revenue metrics logged |

**Phase 5 Gate:** First paying customer OR 3 active pilots.

---

## 8. Anti-Drift Protocol

**You WILL drift.** This protocol prevents it. Inherited from ZPE-Bio, refined for commercial velocity.

### 8.1 Session Start Checklist (MANDATORY)

```
STEP 1: Read RUNBOOK_00_MASTER.md
STEP 2: Check the Phase Gates table — which phase are you in?
STEP 3: Open the corresponding RUNBOOK_0N file
STEP 4: Find last step marked [x] — the next [ ] is YOUR starting point
STEP 5: Read PRD sections referenced by that step
STEP 6: Begin work
```

### 8.2 Mid-Session Re-Grounding (Every 600 Seconds)

```
RE-GROUND 1: What phase am I in? What step?
RE-GROUND 2: Does my current work align with the step description?
RE-GROUND 3: Have I skipped any steps?
RE-GROUND 4: Have any DTs failed since last check?
RE-GROUND 5: Am I introducing code not referenced in the PRD?
RE-GROUND 6: Am I optimising something that doesn't need optimising yet?
RE-GROUND 7: Am I doing something "academically interesting" instead of commercially necessary?
```

### 8.3 Session End Checklist (MANDATORY)

```
END 1: Update Phase Gates table in RUNBOOK_00
END 2: Mark completed steps as [x] in active RUNBOOK
END 3: Write 1-2 sentence summary in "Agent Notes" column
END 4: If any DT failed, document: which DT, output, suspected cause
END 5: Commit with message format: [STEP-N.M] description
END 6: Log to CometML or SESSION_LOG.md
```

### 8.4 Commercial Velocity Check (NEW — Not in ZPE-Bio)

At the end of every phase:

```
VELOCITY 1: Does what I built move us closer to a paying customer?
VELOCITY 2: Could I demo this to an IoT engineer right now? Would they care?
VELOCITY 3: Is there anything blocking a sale that I should fix BEFORE the next phase?
VELOCITY 4: Am I gold-plating? Ship ugly > ship never.
```

---

## 9. Pivot Decision Framework

```
DT FAILED
  └─ Is the failure in the codec logic?
      ├─ YES → Check PT-1 (CR) or PT-2 (NRMSE) triggers
      │    ├─ Trigger fires → PIVOT: update PRD, re-implement
      │    └─ Trigger does not fire → FIX: patch and re-test
      └─ NO → Is the failure in infrastructure/tooling?
           ├─ YES → Fix infrastructure, re-test, do not modify codec
           └─ NO → Is the failure in the test itself?
                ├─ YES → Fix test, document, get user approval
                └─ NO → ESCALATE to user

CRITICAL RULE: Never modify a DT to make it pass.
DTs are the immune system — weakening them kills the project.
```

### 9.1 Joint Trigger Rule (PT-1 + PT-2)

```
PT-1 = TRUE AND PT-2 = TRUE
  → ARCHITECTURE_BREAK
  → Freeze all feature work
  → Evaluate: add entropy coding (arithmetic/ANS), increase magnitude bits, or split modes
  → Re-run DT-01/DT-02 only after rescue completes
```

### 9.2 Gate Integrity Rule (No Silent Relaxation)

If ANY gate threshold is changed (e.g., NRMSE 5% → 10%):
- Update PRD with rationale and data artifact
- Mark results as `PROVISIONAL`
- Do NOT mark phase `PASSED` on relaxed gates without user ratification

---

## 10. Innovation Protocol

### 10.1 At Success Points

```
INNOVATE 1: Log all metrics to CometML
INNOVATE 2: Compare against stretch targets
             - CR > 10x on any dataset? → Document signal characteristics (high RLE opportunity)
             - NRMSE < 1%? → Consider promoting to "lossless-equivalent" claim
INNOVATE 3: Check if a new signal type / dataset should be added to presets
INNOVATE 4: Proceed to next phase
```

### 10.2 At Failure Points

```
INNOVATE 1: Document failure fully (input, output, expected, actual)
INNOVATE 2: Root cause:
             - Fundamental limitation of 8-primitive approach? → Propose architecture change
             - Parameter tuning issue? → Run Pareto sweep
             - Dataset pathology? → Characterise and add to DT-05
INNOVATE 3: Update PRD with findings
INNOVATE 4: Re-implement and re-test
```

---

## 11. File Naming Conventions

| Type | Convention | Example |
|:---|:---|:---|
| Rust source | `snake_case.rs` | `quantise.rs`, `adaptive.rs` |
| Python source | `snake_case.py` | `codec.py`, `presets.py` |
| Test files | `test_<module>.rs` / `test_<module>.py` | `test_codec.rs` |
| DT scripts | `dt<NN>_<snake_name>.py` | `dt01_fidelity.py` |
| Benchmark scripts | `bench_vs_<competitor>.py` | `bench_vs_zstd.py` |
| Config files | `UPPER_SNAKE.toml/.yaml` | `Cargo.toml` |
| Documentation | `UPPER_SNAKE.md` | `RUNBOOK_01_CORE_CODEC.md` |
| Commit messages | `[STEP-N.M] description` | `[STEP-1.4] implement FAST mode encode` |
| Branch names | `phase-N/<feature>` | `phase-1/quantise-trait` |
| CometML experiments | `zpe-iot-phase-N-<description>` | `zpe-iot-phase-2-full-dt-suite` |
| Result files | `<type>_<dataset>_<timestamp>.json` | `dt01_ds02_20260215T143000.json` |

---

## 12. Emergency Procedures

### 12.1 If You Don't Know Where You Are

```
1. Read RUNBOOK_00_MASTER.md
2. Check Phase Gates table
3. If table is empty:
   a. Does zpe-iot/ exist? If no → Phase 0
   b. Does core/src/codec.rs exist? If no → Phase 0 or 1
   c. Run: git log -n 5 to determine last completed step
4. Resume from the identified point
```

### 12.2 If Dependencies Won't Install

```
1. Check Cargo.toml / pyproject.toml versions in PRD §3.2
2. Use pinned versions — do NOT upgrade to latest
3. If pinned version unavailable:
   a. Find closest available version
   b. Document in docs/DEPENDENCY_OVERRIDES.md
   c. Re-run ALL DTs to verify no breakage
```

### 12.3 If Benchmark Datasets Won't Download

```
1. Run: python validation/datasets/download_datasets.py
2. If any dataset fails:
   a. Check README.md for mirror URLs
   b. Skip unavailable dataset — mark as UNAVAILABLE in results
   c. DTs that depend on skipped datasets get status SKIPPED (not FAIL)
   d. A DT is only PASS when ALL datasets are available and pass
```

### 12.4 If CometML Is Unreachable

```
1. Log to docs/SESSION_LOG.md instead (markdown table format)
2. Set environment variable: ZPE_IOT_COMET_OFFLINE=1
3. DT runner MUST NOT fail due to CometML connectivity
4. When CometML is available again, bulk-upload from SESSION_LOG
```

---

## 13. Commercial Execution (Post Phase 5)

### 13.1 Target Customer Profile

| Attribute | Description |
|:---|:---|
| **Company size** | 10-500 employees (IoT/industrial SaaS) |
| **Pain point** | Cellular data costs > $10K/month OR battery life < target |
| **Technical buyer** | Engineering lead / CTO who can evaluate SDK directly |
| **Decision cycle** | < 30 days (engineer-led, not procurement committee) |
| **Budget authority** | Can approve $25K-$100K annual software spend |

### 13.2 Sales Motion

```
1. Engineer discovers zpe-iot (HN, PyPI, crates.io, search)
2. pip install zpe-iot → runs quickstart.py on their data
3. Sees 5-10x compression vs 2-3x from zstd/LZ4
4. Runs benchmark on their production dataset → calculates $ savings
5. Free tier covers evaluation + small deployment
6. Scale triggers Pro tier → sales conversation
7. Embedded OEM → Embedded tier → licensing conversation
```

### 13.3 Revenue Milestones

| Milestone | Target Date | Metric |
|:---|:---|:---|
| M1: First pilot | Phase 5 + 2 weeks | 1 company compressing their data with zpe-iot |
| M2: First revenue | Phase 5 + 4 weeks | First Pro license or consulting engagement |
| M3: 3 paying customers | Phase 5 + 8 weeks | ARR > $0 from 3 distinct companies |
| M4: $10K MRR | Phase 5 + 16 weeks | Recurring monthly revenue |

---

*This document is a living specification. It evolves through recursive falsification and data-driven pivots. Every claim is verified by destruct test. Every decision is logged. Ship ugly > ship never.*

---

## 14. Addendum v1.1 (2026-02-14) — Draconian Integrity + Intersectional Advancement

This addendum is **append-only**. Existing v1.0 sections remain intact for memory continuity.

### 14.1 Memory-Preserving Amendment Protocol

1. Never delete prior requirements.  
2. If behavior changes, add a dated supersession note:
   - Format: `[SUPERSEDED-YYYY-MM-DD by §14.X]`
3. Keep historical guidance visible for traceability, but execute the latest dated rule.
4. Every addendum change must map to at least one falsifiable test or measurable gate.

### 14.2 Evidence Classes and Claim Permissions

| Class | Dataset Evidence | Allowed Claims | Not Allowed |
|:---|:---|:---|:---|
| **E0: PROXY** | Synthetic/proxy-generated stand-ins | Internal tuning, architecture exploration | Public superiority claims |
| **E1: REAL_PUBLIC** | Real public datasets with reproducible provenance | Public benchmark claims with citations | Customer ROI guarantees |
| **E2: REAL_CUSTOMER** | Customer-provided production traces with consent | Commercial ROI claims, pilot conversion claims | None (within legal/privacy constraints) |

**Rule:** PT-6 is `PROVISIONAL` on E0 and only `FINAL` on E1 or E2.

### 14.3 Gate Semantics Upgrade (Draconian Mode)

This section supersedes the permissive SKIP behavior for phase progression.

1. For mandatory gates, `SKIPPED` is treated as `FAIL_GATING`.
2. Mandatory gate set:
   - P0 + P1 DTs for Phase 2 pass
   - DT-16 for benchmark regression in Phase 4 and Phase 5 pre-release
3. `SKIPPED` may exist only in exploratory runs that are explicitly labeled `PROVISIONAL`.
4. A phase cannot be marked `PASSED` if any mandatory DT is `SKIPPED`.

### 14.4 Dataset Provenance Invariants

For DS-01..DS-08, `validation/datasets/manifest.json` must include:

- `provenance_class` (`proxy`, `real_public`, `real_customer`)
- `source_url`
- `license`
- `retrieval_date_utc`
- `raw_sha256`
- `transform_sha256`
- `notes`

**Gate rule:** Phase 4 `PASSED` and Phase 5 launch actions require DS-01..DS-08 at `real_public` or better.

### 14.5 External Publishing Deferral Policy

PyPI, crates.io, and public GitHub push remain deferred until:

1. Draconian gate semantics are implemented and verified.
2. Evidence class is at least E1 for benchmark claims.
3. User ratifies launch readiness.

### 14.6 Intersectional Scientific Workstreams (Falsifiable)

These workstreams are constrained to testable engineering outcomes.

| ID | Intersectional Signal | Engineering Form | Pass Condition |
|:---|:---|:---|:---|
| **WI-1** | Thermodynamics + Information Theory | Entropy-aware token stream staging (direction/magnitude split + entropy coder) | Mean CR improves >= 12% at same NRMSE on E1 suite |
| **WI-2** | Morphogenesis + Linguistics | Motif grammar over direction runs (dictionary of recurring symbolic morphologies) | Token count drops >= 8% without latency regression > 10% |
| **WI-3** | Cellular Automata + Computation | Lightweight local rule predictor for next-direction residual | Residual entropy decreases >= 10% on DS-02/DS-06/DS-08 |
| **WI-4** | Electromagnetism + Spectral Dynamics | Optional curvature/second-delta mode for high-frequency telemetry | Wins at least one current-loss dataset without violating MAX_NRMSE |

### 14.7 New DT Extensions

| DT | Name | Priority | Purpose | Pass Condition |
|:---|:---|:---|:---|:---|
| **DT-17** | Provenance Integrity | P0 | Validate dataset evidence class and hashes | DS-01..DS-08 manifest complete and verified |
| **DT-18** | Strict Gate Enforcement | P0 | Ensure runner fails on mandatory SKIP | Simulated SKIP yields non-zero exit in strict mode |
| **DT-19** | Claim-Tier Compliance | P1 | Prevent E0 claims from being presented as final | Docs/reports carry correct evidence label |
| **DT-20** | Workstream Ablation | P2 | Confirm WI gains are real, not noise | Candidate variant beats control across repeated seeds |
| **DT-21** | Architecture Tightness | P1 | Enforce non-circuitous implementation | No dead paths, no redundant encode/decode loops in hot paths |

### 14.8 Architecture Tightness Constraints

1. No superfluous data passes in critical path (single-pass encode per window).
2. No hidden fallback that converts a missing prerequisite into PASS.
3. Minimize path branching in `core/src/codec.rs`; prefer explicit mode strategy objects.
4. Keep FFI boundary deterministic and allocation-aware.
5. Scripts used for customer demos must compare against declared baselines when the runbook says so.

### 14.9 Updated Ready-to-Sell Definition

`READY_TO_SELL` requires all:

1. `STRICT_DTS_GREEN`: mandatory DTs PASS with zero SKIP.
2. `EVIDENCE_AT_LEAST_E1`: benchmark claims backed by real public datasets.
3. `PT6_FINAL`: competitor parity pass on E1/E2 evidence.
4. `CUSTOMER_DEMO_READY`: demo script produces side-by-side zpe-iot vs baseline comparison + ROI.
5. `USER_RATIFIED`: explicit user approval to publish.

---

## 15. Addendum v1.2 (2026-02-14) — Audit Closure + Data Access Strategy

This addendum is append-only and keeps v1.0/v1.1 as historical memory.

### 15.1 Supersession Notes

- `[SUPERSEDED-2026-02-14 by §15.2]` Any WI retention claim based on non-wire decode paths is provisional.
- `[SUPERSEDED-2026-02-14 by §15.2]` Any relaxed DT threshold not reflected in this PRD constants/governance is provisional.
- `[SUPERSEDED-2026-02-14 by §15.2]` Any public headline claim not matching current active evidence tier is provisional.

### 15.2 Gap-Closure Objectives (Local Code Oriented)

| ID | Gap | Required Closure |
|:---|:---|:---|
| **GC-1** | WI-1 ablation validity | Measure candidate via packed-byte decode path, not stream shortcut; run repeats >= 5; compute gate regression from real strict DT reruns. |
| **GC-2** | Threshold governance drift | Reconcile DT limits with PRD constants; either ratify new limits in constants table or revert DT thresholds. |
| **GC-3** | Claim consistency | Align README/sales headline claims with active evidence-tier metrics (currently E1). |
| **GC-4** | Evidence-label correctness | `FINAL` label is disallowed for any evidence tier with `total=0` datasets. |
| **GC-5** | Demo fairness | Customer demo must provide apples-to-apples latency/compression comparison (native path where available). |
| **GC-6** | Baseline integrity | Regression baseline must be immutable and distinct from current run artifacts. |

### 15.3 Closure Acceptance Criteria

1. New strict DT artifact with all mandatory gates PASS and no SKIP/BLOCKED in mandatory set.
2. PRD constants/governance and DT implementations are numerically consistent.
3. Evidence-tier labeling rule passes static checks:
   - `PROVISIONAL` for E0
   - `FINAL` allowed only when tier dataset count > 0
4. WI-1 decision is re-evaluated with wire-path benchmarking and repeated runs.
5. Public-facing docs and demo output match current evidence-tier truth.

### 15.4 Real Data Priority Matrix (Best ROI for Compression Workstream)

| Priority | Dataset Family | Why It Is High Value | Source Class |
|:---|:---|:---|:---|
| **P1** | Customer production telemetry (real payload traces) | Maximum commercial relevance and conversion power; best predictor of pilot success. | E2 |
| **P1** | Industrial vibration/bearing run-to-failure | Strong structure + clear business pain for predictive maintenance bandwidth costs. | E1/E2 |
| **P1** | Energy/power/voltage minute-level streams | High continuity and repetitive motifs; strong compression opportunity and clear cost model. | E1/E2 |
| **P1** | Mobility/GPS trajectory deltas | Large fleets with transport costs; validates motion-oriented presets. | E1/E2 |
| **P2** | Environmental/weather/air-quality | Broad public availability; stable baseline for deterministic QA. | E1 |
| **P2** | Synthetic adversarial controls | Required for stress testing and falsification, not for commercial claim headlines. | E0 |

### 15.5 Data Access and Token Policy

1. **Hugging Face token (`HF_TOKEN`)**
   - Not required for public repository downloads.
   - Required for private or gated datasets, and any workflow needing authenticated access.
2. **GitHub token (`GH_TOKEN`/PAT)**
   - Not required for normal public clone/raw fetch in low-volume workflows.
   - Required for private repositories and recommended for high-volume API usage due to unauthenticated API rate limits.
3. **Kaggle token (`kaggle.json`)**
   - Required for Kaggle API dataset pulls.
4. Store tokens in local env/secret stores only; never commit tokens or expanded URLs with embedded credentials.

### 15.6 Zer0pa Intersectional Hypothesis Stack (Performance Track)

The following hypotheses are additive workstreams and must pass strict falsification before adoption.

| Hypothesis ID | Intersectional Signal | Proposed Mechanism | Retention Criterion |
|:---|:---|:---|:---|
| **ZH-1** | Thermodynamics + information theory | Encode residuals in derivative domain to reduce effective entropy before bitpack/RLE. | >= 8% mean CR lift on E1 at non-inferior NRMSE and no P0/P1 regressions. |
| **ZH-2** | Morphogenesis + geometry | Multi-scale quantisation (coarse regime + fine local correction) for regime-changing signals. | >= 10% CR lift on vibration/accelerometer presets with stable latency envelope. |
| **ZH-3** | Electromagnetism + periodic systems | Optional periodic predictor stage for quasi-harmonic voltage/current/flow traces. | >= 12% CR lift on periodic datasets and no decode determinism violations. |
| **ZH-4** | Linguistics + symbolic computation | Learn compact token grammar over primitive sequences (bounded dictionary, deterministic). | >= 6% CR lift with <= 5% decode latency increase and deterministic reconstruction. |
| **ZH-5** | Cellular automata + local update rules | Window-local state transition compression for low-complexity spatially correlated channels. | Benefit holds across >= 3 dataset families; otherwise reject as overfit. |

### 15.7 Engineering Elegance Constraints (No Circuitous Code)

1. Hot path remains single-pass and allocation-aware.
2. Any new stage must be feature-flagged, benchmarked, and removable without API breakage.
3. No hidden fallback may translate missing prerequisites into PASS-equivalent outcomes.
4. Benchmark and demo paths must be method-fair across competitors.
5. Complexity budget: remove or collapse dead/duplicate branches when adding any new stage.

### 15.8 Language/Runtime Performance Position

1. Rust core remains primary for production-critical compression/decompression due to deterministic performance, memory control, and embedded portability.
2. Python remains orchestration and SDK UX layer; heavy compute work should not migrate from Rust hot paths.
3. C/C++ rewrite is not justified at current maturity unless profiling proves an irreducible Rust bottleneck.
4. Next local optimization focus:
   - data-layout and branch predictability in codec hot loops,
   - optional SIMD where safe and reproducible,
   - tighter benchmark harness fairness and artifact metadata.

### 15.9 Real-Public Dataset Source Catalog (Execution Seed)

| Primitive Coverage | Source | URL | Access Notes |
|:---|:---|:---|:---|
| temperature/pressure/generic | NOAA CDO/NCEI | https://www.ncei.noaa.gov/cdo-web/ | NOAA CDO API calls require NOAA token; bulk/public assets are broadly accessible. |
| flow | USGS Water Data APIs | https://api.waterdata.usgs.gov/ | Public API for streamflow and related hydro time-series. |
| vibration | CWRU Bearing Data Center | https://engineering.case.edu/bearingdatacenter/welcome | Public academic dataset, strong for fault and periodicity analysis. |
| vibration/accelerometer | NASA C-MAPSS / PHM08 | https://c3.ndc.nasa.gov/dashlink/resources/139/ | Run-to-failure multichannel trajectories. |
| accelerometer | UCI WISDM | https://archive.ics.uci.edu/ml/datasets/WISDM_Smartphone_and_Smartwatch_Activity_and_Biometrics_Dataset_ | Human-motion inertial signals. |
| voltage/current | UCI Household Electric Power Consumption | https://archive.ics.uci.edu/dataset/235/individual | Long-span power draw stream with minute resolution. |
| gps_track | Microsoft GeoLife | https://www.microsoft.com/en-us/research/project/geolife-building-social-networks-using-human-location-history/downloads/ | Longitudinal GPS trajectories. |
| generic anomaly streams | Numenta NAB | https://github.com/numenta/NAB | Mixed real telemetry and anomaly labels. |

### 15.10 Token Guidance Clarification

1. Hugging Face:
   - Public repo download: authentication optional.
   - Private or gated repo download: token required.
2. GitHub:
   - Public clone/raw access: token optional.
   - API-heavy workflows/private repos: authenticated token recommended or required.
3. Kaggle:
   - Kaggle API access requires credentials (`KAGGLE_USERNAME`, `KAGGLE_KEY`).
4. Operational rule:
   - Prefer no-token public pulls first.
   - Fall back to scoped tokens only when a source is gated/private or rate-limited for your run volume.

### 15.11 Agent Access Preflight Gate (Upfront)

Before any execution session proceeds past setup:

1. Confirm working directory:
   - `/Users/zer0pa-build/ZPE IoT/zpe-iot`
2. Confirm required CLIs:
   - `gh` (required for GitHub auth checks)
   - `kaggle` (required for Kaggle API pulls)
   - `huggingface-cli` optional; HTTP checks with `HF_TOKEN` are acceptable fallback
3. Confirm credential visibility in current shell:
   - GitHub: `gh auth status` OR valid `GH_TOKEN`
   - Kaggle: `KAGGLE_API_TOKEN` (supported), with legacy compatibility via `KAGGLE_USERNAME` + `KAGGLE_KEY` if needed by tools
   - Hugging Face: valid `HF_TOKEN` for private/gated assets; public pulls can run tokenless
4. Record preflight result in session log:
   - `ACCESS_READY` or `ACCESS_BLOCKED:<reason>`

No phase gate should be marked complete if prerequisite data/tool access was missing and not explicitly logged.

## 16. Addendum v1.3 (2026-02-14C) — Local Draconian Closure Ratifications

This addendum is append-only and keeps v1.0/v1.1/v1.2 intact.

### 16.1 Supersession Notes

- `[SUPERSEDED-2026-02-14C by §16.2]` Any DT threshold drift that is not mapped to a single auditable source-of-truth file is provisional.
- `[SUPERSEDED-2026-02-14C by §16.3]` Any DT-16 baseline selection that depends on "latest file" behavior is invalid for strict gating.

### 16.2 Threshold Ratification (Date-Stamped)

Ratified threshold updates for E1-calibrated DT behavior:

1. `DT-04` noisy NRMSE limits:
   - default remains `MAX_NRMSE_NOISY = 0.08`
   - dataset-specific ratified calibrations:
     - `DS-03: 0.12`
     - `DS-08: 0.14`
   - rationale: DS-03/DS-08 real-public channels carry higher stochastic variance in injected-noise windows; calibration avoids false architectural rejection while preserving strict failure on materially unstable reconstruction.
2. `DT-12` preset floor ratification:
   - `PRESET_MIN_MEAN_CR = 3.8`
   - `PRESET_MAX_MEAN_NRMSE = 0.05`
   - rationale: enforce practical E1 floor for cross-preset viability without weakening fidelity bound.

Source-of-truth file for DT thresholds:
- `zpe-iot/validation/destruct_tests/thresholds.py`

Audit mapping artifact:
- `zpe-iot/docs/THRESHOLD_GOVERNANCE_AUDIT.md`

### 16.3 DT-16 Baseline Immutability Contract (Ratified)

`DT-16` must resolve an explicit baseline identity by tag and verify hash integrity before comparison.

Required structure:
- `validation/results/baseline/<baseline_tag>/bench_summary.json`
- `validation/results/baseline/<baseline_tag>/manifest.json`
- `validation/results/baseline/ACTIVE_BASELINE_TAG` (optional local pointer)

Invalid behavior:
- Any floating "latest baseline" discovery.

### 16.4 Evidence-Tier Label Rule (Ratified)

For benchmark summaries:
- If `total == 0` datasets for a tier: label/status must be `NOT_AVAILABLE`.
- `FINAL` is legal only when `total > 0` and evidence class is E1/E2.
- `PROVISIONAL` is legal only when `total > 0` and evidence class is E0.

### 16.5 ZH Prototype Governance Rule

Intersectional ZH prototypes (`ZH-1..ZH-*`) are retainable only when all are true:
1. feature remains flag-gated and default-off until ratified,
2. strict mandatory gates remain green (no introduced mandatory failures),
3. E1 aggregate metrics improve at or above the workstream threshold,
4. wire-path measurement protocol (`encode bytes -> decode bytes`) with repeats `>= 5` is evidenced.

## 17. Addendum v1.4 (2026-02-19) — Enterprise Operationalisation Transition

This addendum is append-only and keeps all prior PRD history intact.

### 17.1 Supersession Notes

- `[SUPERSEDED-2026-02-19 by §17.2]` \"technically hardening-complete\" is not sufficient for enterprise-grade packaging status.
- `[SUPERSEDED-2026-02-19 by §17.2]` Packaging readiness claims are provisional until enterprise program gates are passed.

### 17.2 Enterprise Program Authority

The active execution authority for enterprise completion is:

- `PRD_06_ENTERPRISE_EXECUTION_v1.0.md`

This program defines phases `E0..E9` for repository formalization, packaging hardening, coherence/cohesion cleanup, CI/security maturity, and release candidate assembly.

### 17.3 Enterprise Exit Criteria (Ratified)

Enterprise transition is complete only when all are true:

1. Canonical repository topology is explicit and documented.
2. Packaging builds are warning-free and install-smoke tested.
3. Metric semantics are explicit and non-ambiguous across DT and benchmark outputs.
4. CI gates enforce Rust/Python quality and strict DT smoke checks.
5. Security and provenance artifacts (including SBOM/release manifest) are generated for release candidate.
6. Final strict DT and benchmark split artifacts are green and evidence-labeled.
7. External publish remains deferred until explicit user ratification.

### 17.4 Enterprise Execution Snapshot (2026-02-19)

Execution against `PRD_06_ENTERPRISE_EXECUTION_v1.0.md` completed locally with evidence:

1. Final strict DT artifact: `zpe-iot/validation/results/dt_results_20260219T030940.json`
   - Summary: `PASS=21, FAIL=0, SKIPPED=0, BLOCKED=0`.
2. Final benchmark split artifacts:
   - `zpe-iot/validation/results/bench_summary_E0_proxy_20260219T030604.json`
   - `zpe-iot/validation/results/bench_summary_E1_real_public_20260219T030604.json`
   - `zpe-iot/validation/results/bench_summary_E2_real_customer_20260219T030604.json`
3. Security/provenance artifacts:
   - `zpe-iot/validation/results/vulnerability_scan_20260219T003747.json`
   - `zpe-iot/validation/results/sbom_20260219T011216.json`
   - `zpe-iot/validation/results/release_manifest_20260219T011216.json`
4. Release candidate bundle assembled:
   - `zpe-iot/release/RC_20260219T031240/`
5. External publish actions remain deferred pending explicit user ratification.

## 18. Addendum v1.5 (2026-02-20) — Chemosense Extension Ratification

This addendum is append-only and keeps v1.0-v1.4 intact.

### 18.1 Scope Ratification

Ratified local extension scope:

1. Smell modality packetization under `SMELL_TYPE_BIT = 0x0200`.
2. Taste modality packetization under `TASTE_TYPE_BIT = 0x0400`.
3. Deterministic taste-smell-touch fusion scheduler with strict packet ordering (`taste -> smell -> touch`).
4. No external runtime dependency on upstream source paths.

Canonical in-repo location:
- `zpe-iot/python/zpe_iot/chemosense/`

### 18.2 Architectural Guardrails

1. Copy-only ingestion rule: imported capability modules must be copied into repository; symlinked dependencies are invalid.
2. Import locality rule: references to `artifacts.packetgram.*` are non-compliant post-ratification.
3. Bit-domain separation rule: modality type bits must remain collision-free within extension payload high bits.
4. Deterministic fallback rule: adaptive taste temporal coding must always decode to a valid coarse/fine semantic stream.

### 18.3 Validation Ratification

Local technical closure is ratified only when all are true:

1. Python full gate:
   - `pytest -q` passes
   - coverage threshold `>= 85%` is met
2. Rust quality gate:
   - `cargo test` passes
   - `cargo clippy -- -D warnings` passes
3. Strict destructive gate:
   - `validation/destruct_tests/run_all_dts.py --strict-gates` yields no FAIL/SKIPPED/BLOCKED on mandatory set

Ratified evidence snapshot:

1. Strict DT:
   - `zpe-iot/validation/results/dt_results_20260220T030203.json`
   - `PASS=21, FAIL=0, SKIPPED=0, BLOCKED=0, NOT_IMPLEMENTED=0, TIMEOUT=0`
2. Python test gate:
   - `41 passed`
   - coverage `87.76%`

### 18.4 Product Surface Additions

1. Python namespace:
   - `import zpe_iot.chemosense`
2. CLI executable proof path:
   - `zpe-iot chemosense-smoke --json`
3. Documentation:
   - `zpe-iot/docs/CHEMOSENSE_EXTENSION.md`
   - quickstart updates in `zpe-iot/README.md` and `zpe-iot/python/README.md`

### 18.5 Commercial/Publish Constraint

This addendum does not supersede publish governance:

1. Public publish remains user-ratified only.
2. E2 customer-data evidence remains external-input dependent and is not claimable as FINAL until present.

## 19. Addendum v1.6 (2026-02-20B) — Touch + Mental Expansion Authority

This addendum is append-only and preserves all prior PRD history.

### 19.1 Scope Extension

Ratified next-stage extension scope:

1. Integrate **touch modality** as first-class chemosense package module.
2. Integrate **mental modality** as first-class chemosense package module.
3. Preserve and validate modality bit partitioning in mixed streams:
   - mental `0x0100`
   - smell `0x0200`
   - taste `0x0400`
   - touch `0x0800`

### 19.2 Rationale

1. Touch and mental source stacks are available and test-backed in the multimodality stream.
2. First chemosense pass prioritized smell+taste closure and strict gate stability.
3. Touch/mental integration is now an explicit authorized continuation, not an ad hoc fork.

### 19.3 Technical Guardrails

1. Copy-only ingestion; no symlink dependency.
2. All `from source.*` imports must be rewritten to local in-repo package paths.
3. No gate weakening is permitted to absorb new modality surface area.
4. Placeholder touch packet helpers must be replaced by canonical touch codec path.
5. Mental 8-dir and D6-12 profile semantics must remain deterministic under pack/unpack.

### 19.4 Execution Authority

The governing execution PRD for this expansion is:

- `PRD_08_TOUCH_MENTAL_ENTERPRISE_v1.0.md`

### 19.5 Publish Governance

This addendum does not authorize public launch by itself. Publish remains deferred until explicit user ratification.
