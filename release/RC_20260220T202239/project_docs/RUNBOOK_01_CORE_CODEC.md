# RUNBOOK_01_CORE_CODEC.md — Phase 0+1: Setup & Core Codec Implementation

**STOP.** Have you read `RUNBOOK_00_MASTER.md`? If no, read it NOW.
**What phase is marked in the Phase Gates table?** If not Phase 0 or 1, you are in the wrong runbook.

---

## Phase 0+1 Objective

Create the repository skeleton, implement the generalised 8-primitive codec in both Rust (canonical) and Python (reference), validate cross-platform parity, and pass all P0 destruct tests on synthetic data.

**Input:** PRD v1.0, Legacy Work codec (read-only reference)
**Output:** Working codec passing DT-01..07, DT-11, DT-13 on synthetic signals, all metrics logged
**Gating DTs:** DT-01 (Fidelity), DT-02 (Compression Floor), DT-03 (Determinism), DT-04 (Noise), DT-05 (Pathological), DT-06 (RAM), DT-07 (Latch Freedom), DT-11 (Cross-Platform), DT-13 (Bitpack Integrity)

---

## Step 0: Repository Setup

### Step 0.1: Create Repository

- [x] **Action:** Create project directory and initialise git.
```bash
cd "/Users/prinivenpillay/ZPE IoT"
mkdir -p zpe-iot
cd zpe-iot
git init
git checkout -b main
```
- [x] **Verify:** `pwd` outputs `/Users/prinivenpillay/ZPE IoT/zpe-iot` AND `.git/` exists.

### Step 0.2: Create Directory Skeleton

- [x] **Action:** Create ALL directories per PRD §3.1. Do not skip any.
```bash
mkdir -p core/src
mkdir -p core/tests
mkdir -p python/zpe_iot
mkdir -p python/tests
mkdir -p c
mkdir -p validation/destruct_tests
mkdir -p validation/benchmarks
mkdir -p validation/datasets
mkdir -p validation/results
mkdir -p examples/python
mkdir -p examples/rust/embedded_demo
mkdir -p examples/c/arduino_demo
mkdir -p scripts
mkdir -p docs
```
- [x] **Verify:** `find . -type d | sort` matches PRD §3.1 layout.

### Step 0.3: Create Cargo.toml

- [x] **Action:** Create `core/Cargo.toml`:
```toml
[package]
name = "zpe-iot"
version = "0.1.0"
edition = "2021"
description = "8-primitive geometric compression SDK for IoT sensor data"
license = "MIT"
keywords = ["compression", "iot", "sensor", "embedded", "no_std"]

[lib]
crate-type = ["staticlib", "cdylib", "rlib"]

[features]
default = ["std"]
std = []
embedded = []

[dependencies]
heapless = "0.8"

[dev-dependencies]
proptest = "1.4"
```
- [x] **Verify:** `cd core && cargo check` passes.

### Step 0.4: Create pyproject.toml

- [x] **Action:** Create `python/pyproject.toml`:
```toml
[project]
name = "zpe-iot"
version = "0.1.0"
description = "8-primitive geometric compression SDK for IoT sensor data"
license = {text = "MIT"}
requires-python = ">=3.9"
dependencies = [
    "numpy>=1.24",
    "click>=8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "hypothesis>=6.0",
    "comet_ml>=3.35",
    "matplotlib>=3.7",
    "zstandard>=0.22",
    "lz4>=4.3",
]

[project.scripts]
zpe-iot = "zpe_iot.cli:main"

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
testpaths = ["tests"]
```
- [x] **Verify:** `cd python && pip install -e ".[dev]"` passes.

### Step 0.5: Create DT Script Stubs

- [x] **Action:** Create placeholder for every DT (PRD §5.2):
```bash
cd validation/destruct_tests
for i in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16; do
  touch "dt${i}_placeholder.py"
done
```
- [x] **Verify:** 16 files exist in `validation/destruct_tests/`.

### Step 0.6: Create DT Runner

- [x] **Action:** Create `validation/destruct_tests/run_all_dts.py`.

This MUST follow the exact pattern from Legacy Work `RUNBOOK_02_FALSIFICATION.md` Step 0.2.

Key requirements:
- Accept `--priority P0|P1|P2` and `--dt N N N` flags
- For each DT: find script, run subprocess, capture exit code (0=PASS, non-zero=FAIL)
- Save timestamped JSON to `validation/results/`
- Print summary table with pass/fail counts
- Check P0 gate: if any P0 fails, print warning "DO NOT proceed to next phase"
- Attempt CometML logging; fall back to `docs/SESSION_LOG.md` if unavailable

DT priority map:
```python
DT_PRIORITY = {
    1: "P0", 2: "P0", 3: "P0", 4: "P0", 5: "P0",
    6: "P0", 7: "P0", 8: "P1", 9: "P1", 10: "P1",
    11: "P1", 12: "P1", 13: "P1", 14: "P1", 15: "P1",
    16: "P2",
}

DT_NAMES = {
    1: "Fidelity Gate", 2: "Compression Floor", 3: "Determinism",
    4: "Noise Robustness", 5: "Pathological Inputs", 6: "RAM Budget",
    7: "Latch Freedom", 8: "DC Torture", 9: "Latency",
    10: "Monotonicity", 11: "Cross-Platform Parity", 12: "Preset Coverage",
    13: "Bitpack Integrity", 14: "CRC Detection", 15: "Adaptive Stability",
    16: "Benchmark Regression",
}
```

- [x] **Verify:** `python run_all_dts.py` runs and shows all 16 DTs as `NOT_IMPLEMENTED`.

### Step 0.7: Copy Reusable Legacy Code

- [x] **Action:** Read (do NOT copy directly) these legacy files and use them as reference for implementation:
  - `Legacy Work/zpe-bio/core/rust/src/rle.rs` → base for `core/src/rle.rs`
  - `Legacy Work/zpe-bio/core/rust/src/ffi.rs` → base for `core/src/ffi.rs`
  - `Legacy Work/zpe-bio/python/zpe_bio/codec.py` → reference for `python/zpe_iot/codec.py`

The RLE module can be reused nearly as-is. All other modules must be generalised per PRD §2.

- [x] **Verify:** `cargo check` and `pip install -e .` both still pass after adding files.

### Step 0.8: Initial Commit

- [x] **Action:**
```bash
git add -A
git commit -m "[STEP-0.8] Phase 0: repository skeleton and tooling"
```
- [x] **Verify:** `git log --oneline` shows commit.
- [x] **Log:** Record Phase 0 completion in CometML or `docs/SESSION_LOG.md`.

---

## Step 1: Rust Core Implementation

### Step 1.1: Implement `core/src/lib.rs` — Public API Surface

- [x] **Action:** Create the root library file.

```rust
// core/src/lib.rs
#![cfg_attr(feature = "embedded", no_std)]
#![cfg_attr(feature = "embedded", no_main)]

pub mod quantise;
pub mod rle;
pub mod magnitude;
pub mod adaptive;
pub mod codec;
pub mod bitpack;
pub mod presets;
pub mod ffi;

pub use codec::{encode, decode_into, Config, Mode, EncodedStream};
pub use presets::Preset;
```

- [x] **Verify:** `cargo check` passes.

### Step 1.2: Implement `core/src/quantise.rs` — Trait-Based Quantiser

- [x] **Action:** Implement generalised quantiser per PRD §2.4.

Key requirements:
- `Quantiser` trait with `fn quantise(&self, delta: f64, threshold: f64) -> u8`
- `DefaultQuantiser` struct with configurable `bands: [f64; 3]`
- Direction mapping: 0=FLAT, 1-4=RISE (gentle→extreme), 5-7=FALL (extreme→gentle)
- MUST match Python implementation bit-for-bit

Reference: Legacy `quantise.rs` (but replace hardcoded ECG thresholds with `bands` parameter).

- [x] **Verify:** Unit tests for all 8 direction codes. Test edge cases at exact threshold boundaries.

### Step 1.3: Implement `core/src/magnitude.rs` — Log-Magnitude Table

- [x] **Action:** Implement magnitude quantisation per PRD §2.5.

Key requirements:
- `LOG_BASE: f64 = 1.091928`
- `LOG_MAG_TABLE: [u64; 64]` generated at compile time (or const fn)
- `fn find_magnitude(abs_delta: f64, step: f64) -> u8` — returns index 0-63
- Linear search (64 entries is small enough; binary search adds complexity for no gain)

Reference: Legacy `codec.py` LOG_MAG_TABLE.

- [x] **Verify:** Table matches formula: `TABLE[i] == round(1.091928^i)` for all i in 0..63.

### Step 1.4: Implement `core/src/adaptive.rs` — Threshold Envelope

- [x] **Action:** Implement adaptive threshold per PRD §2.6.

Key requirements:
- `fn update_envelope(envelope: f64, abs_delta: f64, alpha: f64) -> f64`
- `fn compute_threshold(envelope: f64, k: f64, thr_min: f64, thr_max: f64) -> f64`
- `thr_max` is NEW (not in legacy) — prevents threshold runaway on sensor spikes

Reference: Legacy `codec.py` adaptive logic, but add `thr_max` ceiling.

- [x] **Verify:** Unit test: envelope correctly tracks synthetic sinusoid. Threshold stays within [THR_MIN, THR_MAX].

### Step 1.5: Implement `core/src/rle.rs` — Run-Length Encoding

- [x] **Action:** Port from legacy `rle.rs` with minimal changes.

Key requirements:
- `fn compress<const N: usize>(tokens: &[(u8, u8)]) -> heapless::Vec<(u8, u8, u16), N>`
- `fn decompress(rle: &[(u8, u8, u16)], output: &mut [(u8, u8)]) -> usize`
- Handle u16::MAX count (saturate, do not wrap)
- Zero heap allocation

Reference: Legacy `rle.rs` — nearly identical.

- [x] **Verify:** Round-trip: decompress(compress(x)) == x for random token sequences.

### Step 1.6: Implement `core/src/codec.rs` — Encode + Decode

- [x] **Action:** Implement the full encode/decode pipeline per PRD §2.3.

Key requirements:
- `pub struct Config { mode, threshold, step, bands, adaptive, thr_min, thr_max, alpha, k }`
- `pub struct EncodedStream<const N: usize>` with: rle_tokens, start_value, step, mode, sample_count, metadata
- `pub fn encode<const N: usize>(samples: &[f64], config: &Config) -> Result<EncodedStream<N>, CodecError>`
- `pub fn decode_into(stream: &EncodedStream<impl AsRef<[(u8,u8,u16)]>>, output: &mut [f64]) -> Result<usize, CodecError>`
- FAST mode: direction only, magnitude fixed to 1
- BALANCED mode: direction + log-magnitude
- Adaptive threshold: update per sample when config.adaptive == true
- Auto-step: if config.step == 0.0, compute `std(samples) / 64` from first window

Reference: Legacy `codec.rs`, but use trait-based quantiser and configurable bands.

- [x] **Verify:** DT-03 (determinism) passes on 10,000 random seeds.

### Step 1.7: Implement `core/src/bitpack.rs` — Bit Packing + CRC

- [x] **Action:** Implement wire format per PRD §2.8.

Key requirements:
- `fn pack(stream: &EncodedStream, output: &mut [u8]) -> Result<usize, PackError>`
- `fn unpack(bytes: &[u8]) -> Result<EncodedStream, UnpackError>`
- Header: magic (0x5A50), version (0x01), flags (mode, preset, adaptive)
- Metadata: sample_count (u16), start_value (f32), step (f16 or u16 fixed-point)
- Payload: FAST = 1 byte/token (3+5 bits), BALANCED = 2 bytes/token (3+6+7 bits)
- CRC-16-CCITT (poly 0x1021) over entire packet

- [x] **Verify:** DT-13 (bitpack integrity): pack → unpack round-trip on 10,000 random streams.

### Step 1.8: Implement `core/src/presets.rs` — Signal Presets

- [x] **Action:** Implement all 9 presets from PRD §2.7.

```rust
pub enum Preset {
    Temperature,
    Vibration,
    Accelerometer,
    Pressure,
    GpsTrack,
    Voltage,
    Current,
    Flow,
    Generic,
}

impl Preset {
    pub fn config(&self) -> Config { ... }
}
```

Each preset returns a `Config` with values from PRD §2.7 table.

- [x] **Verify:** All 9 presets instantiate without panic. Each produces a valid Config.

### Step 1.9: Implement `core/src/ffi.rs` — C FFI Bindings

- [x] **Action:** Expose C-callable API.

Key functions:
- `zpe_iot_encode(samples, n, config, result) -> i32`
- `zpe_iot_decode(result, output, n) -> i32`
- `zpe_iot_preset_vibration() -> zpe_iot_config_t`
- (one preset function per signal type)

Reference: Legacy `ffi.rs` pattern.

- [x] **Verify:** `cargo build` produces `.a` and `.so`/`.dylib`. `cbindgen` generates `zpe_iot.h`.

---

## Step 2: Python Reference Implementation

### Step 2.1: Implement `python/zpe_iot/__init__.py`

- [x] **Action:** Public API:
```python
from .codec import encode, decode, Config, Mode, EncodedStream
from .presets import Preset
__version__ = "0.1.0"
```

### Step 2.2: Implement `python/zpe_iot/codec.py`

- [x] **Action:** Pure-Python reference codec matching Rust behaviour exactly.

Requirements:
- `Config` dataclass: mode, threshold, step, bands, adaptive, thr_min, thr_max, alpha, k
- `EncodedStream` dataclass: rle_tokens, start_value, step, mode, sample_count
- `encode(samples, config=None, preset=None, **kwargs) -> EncodedStream`
- `decode(stream) -> np.ndarray`
- `compute_nrmse(original, reconstructed) -> float`
- `compute_cr(stream, original_samples) -> float`
- Auto-step when step not provided
- FAST and BALANCED modes
- Adaptive threshold with THR_MAX ceiling

Reference: Legacy `codec.py`, generalised per PRD §2.

- [x] **Verify:** Unit tests pass. Round-trip on synthetic sinusoid: NRMSE < 5%, CR > 3x.

### Step 2.3: Implement `python/zpe_iot/presets.py`

- [x] **Action:** All 9 presets from PRD §2.7.
- [x] **Verify:** Each preset returns valid Config.

### Step 2.4: Implement `python/zpe_iot/cli.py`

- [x] **Action:** CLI with click:
```
zpe-iot compress INPUT --preset PRESET --output OUTPUT [--mode MODE] [--threshold THR]
zpe-iot decompress INPUT --output OUTPUT
zpe-iot benchmark INPUT --compare zstd,lz4,zlib [--preset PRESET]
zpe-iot info INPUT  (show compression stats)
```

- [x] **Verify:** `zpe-iot compress` and `zpe-iot decompress` round-trip a CSV file.

### Step 2.5: Implement `python/zpe_iot/_native.py` — Rust FFI Bindings

- [x] **Action:** Use `cffi` to wrap the C FFI from Step 1.9.
- [x] **Verify:** `_native.encode(samples)` matches `codec.encode(samples)` bit-for-bit.

### Step 2.6: Implement `python/tests/test_codec.py`

- [x] **Action:** Property-based tests using Hypothesis:
  - Determinism: encode(x) == encode(x) for 1000 random signals
  - Fidelity: NRMSE < 5% for BALANCED mode on random signals
  - Compression: CR > 1.0 for all signals (never expand)
  - Round-trip: decode(encode(x)) produces valid output with len == len(x)
  - Monotonicity: higher threshold → higher CR

- [x] **Verify:** `pytest python/tests/` — all green.

### Step 2.7: Implement `python/tests/test_parity.py` — Cross-Platform

- [x] **Action:** Compare Python encode output with Rust FFI encode output on 100 test vectors.
- [x] **Verify:** DT-11 passes: all 100 vectors bit-identical.

---

## Step 3: Run P0 Gate

### Step 3.1: Implement P0 Destruct Tests

- [x] **Action:** Implement DT-01 through DT-07 per PRD §5.2.

Each DT script MUST:
- Have docstring with DT number, PRD ref, pass condition
- Exit 0 for PASS, 1 for FAIL
- Print clear PASS/FAIL per test case
- Attempt CometML logging; fall back gracefully

For Phase 1, DT-01 and DT-02 run on **synthetic datasets** (DS-09, DS-10) and any locally generated signal types. Full dataset suite runs in Phase 2.

### Step 3.2: Run P0 Gate

- [x] **Action:**
```bash
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot"
python validation/destruct_tests/run_all_dts.py --priority P0
```

- [x] **Verify:** ALL P0 DTs PASS.

If ANY P0 DT fails:
```
1. DO NOT proceed to Phase 2
2. Read failure output
3. Consult Pivot Decision Framework in RUNBOOK_00 §4
4. Fix and re-test
5. Re-run ALL P0 DTs (not just the fixed one)
```

### Step 3.3: Also Run P1 Parity & Bitpack DTs

- [x] **Action:**
```bash
python validation/destruct_tests/run_all_dts.py --dt 11 13
```

- [x] **Verify:** DT-11 (Python-Rust parity) and DT-13 (bitpack integrity) both PASS.

---

## Phase 0+1 Completion Gate

- [x] ALL P0 DTs pass (DT-01 through DT-07) on synthetic data
- [x] DT-11 pass (Python-Rust parity)
- [x] DT-13 pass (bitpack integrity)
- [x] Python `pip install -e .` works
- [x] Rust `cargo test` passes
- [x] `zpe-iot compress` / `zpe-iot decompress` CLI works
- [x] All 9 presets instantiate without error
- [x] Results saved to `validation/results/`
- [x] Phase Gates table in RUNBOOK_00 updated
- [x] Session logged to CometML or SESSION_LOG.md
- [x] Git commit: `[PHASE-1] Core codec complete, P0 gate passed`

---

## Addendum A (2026-02-14): Architecture Tightness Sprint (ACTIVE)

This addendum is memory-preserving: legacy steps remain valid historical record.

### Step A.1: Hot-Path Simplicity Audit

- [x] **Action:** Audit `core/src/codec.rs`, `core/src/bitpack.rs`, and `core/src/rle.rs` for redundant passes, duplicate transforms, and unnecessary branching in encode/decode hot paths.
- [x] **Verify:** Produce `docs/ARCH_TIGHTNESS_AUDIT.md` with:
  1. Removed redundancies
  2. Complexity delta (before/after)
  3. Any trade-offs in readability/performance

### Step A.2: Deterministic Error Surface Audit

- [x] **Action:** Ensure missing prerequisites cannot silently return a PASS-equivalent result in production-critical logic.
- [x] **Verify:** Explicit fail-fast or explicit `PROVISIONAL` labeling exists for each fallback path.

### Step A.3: Interface Minimalism

- [x] **Action:** Review public API and examples for accidental double-work patterns (for example, repeated encode calls in a single quickstart path).
- [x] **Verify:** Examples and API usage paths demonstrate single-pass, non-circuitous flow.

### Step A.4: Tightness Regression Checks

- [x] **Action:** Re-run:
```bash
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot/core"
cargo test
cargo clippy -- -D warnings
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot/python"
pytest -q
```
- [x] **Verify:** All checks green with no quality regressions.

### Addendum A Completion Gate

- [x] `docs/ARCH_TIGHTNESS_AUDIT.md` exists and is evidence-backed
- [x] No identified superfluous hot-path logic remains unresolved
- [x] Core tests and lint pass

---

## Addendum B (2026-02-14B): Primitive-Path Performance Sprint (ACTIVE)

This addendum is append-only and extends architecture-tightness into measurable performance work.

### Step B.1: Hot-Path Profiling Baseline

- [ ] **Action:** Record baseline profiles for encode/decode in Rust core on representative DS-01..DS-08 slices.
- [ ] **Action:** Capture top CPU hotspots, allocations, and branch-heavy regions.
- [ ] **Verify:** Save profile summary artifact under `docs/perf/` with timestamp and command lines.

### Step B.2: No-Superfluous-Work Refactor

- [ ] **Action:** Remove or collapse any redundant transform/iteration in `core/src/codec.rs` and `core/src/bitpack.rs`.
- [ ] **Action:** Ensure data traversal remains single-pass per stage where feasible.
- [ ] **Verify:** Bench micro-tests show non-regressing or improved latency with identical decode outputs.

### Step B.3: Feature-Flagged Intersectional Prototype

- [ ] **Action:** Implement one prototype from PRD §15.6 (`ZH-1`, `ZH-2`, or `ZH-3`) behind explicit feature flag.
- [ ] **Action:** Keep public API stable; no behavior change unless flag is enabled.
- [ ] **Verify:** Full unit/property/parity tests remain green with flag off and on.

### Step B.4: Tightness Regression Pack

- [ ] **Action:** Re-run:
```bash
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot/core"
cargo test
cargo clippy -- -D warnings
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot/python"
pytest -q
```
- [ ] **Action:** Re-run strict DT suite from project root.
- [ ] **Verify:** No mandatory gate regression and no new complexity debt recorded.

### Addendum B Completion Gate

- [ ] Hot-path profile baseline artifact exists
- [ ] Superfluous-work reductions are documented and validated
- [ ] At least one feature-flagged intersectional prototype is benchmarked
- [ ] Strict DT and parity checks remain green

---

## Addendum C (2026-02-20): Chemosense Modality Extension Sprint (ACTIVE)

This addendum is append-only and preserves all earlier execution history.

### Step C.1: In-Repo Modality Copy and Isolation

- [x] **Action:** Copy required smell/taste modality modules into `python/zpe_iot/chemosense/` (no symlinks).
- [x] **Verify:** Tree exists with `common/`, `smell/`, `taste/` and executes without external source-tree dependency.

### Step C.2: Local Import Rewire

- [x] **Action:** Replace external `artifacts.packetgram.*` imports with local `..common.*`.
- [x] **Verify:** `rg "artifacts\\.packetgram" python/zpe_iot/chemosense` returns no matches.

### Step C.3: SDK/CLI Surface Integration

- [x] **Action:** Add package entrypoints and root namespace access.
- [x] **Action:** Add executable smoke path via CLI command.
- [x] **Verify:**
  1. `python/zpe_iot/__init__.py` exposes `chemosense`.
  2. `zpe-iot chemosense-smoke --json` returns deterministic event counts.

### Step C.4: Branch-Level Validation Pack

- [x] **Action:** Add deterministic roundtrip tests for smell, taste, and fusion scheduler.
- [x] **Action:** Add branch-level coverage tests across quantize/adaptation/augment/pack/codebook paths.
- [x] **Verify:** `pytest -q` passes with repository coverage threshold intact.

### Step C.5: Regression and Tightness Gates

- [x] **Action:** Re-run
```bash
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot/core"
cargo test
cargo clippy -- -D warnings
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot/python"
source .venv/bin/activate && pytest -q
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot"
source python/.venv/bin/activate && python validation/destruct_tests/run_all_dts.py --strict-gates
```
- [x] **Verify:** No regression in strict gate counts (`PASS=21, FAIL=0, SKIPPED=0`).

### Addendum C Completion Gate

- [x] Copied chemosense stack is fully local and import-clean.
- [x] Python test gate remains above threshold (`87.76%`).
- [x] Rust test/lint gates are green.
- [x] Strict DT suite remains fully green.

**End of RUNBOOK_01. Next: RUNBOOK_02_FALSIFICATION.md**

## Addendum C.1 (2026-02-20): Chemosense Enterprise Hardening Delta (PRD-07)

This continuation is append-only and does not modify prior Addendum C history.

### Step C.6: Contract-Surface Hardening

- [x] **Action:** Added stable chemosense contract layer with explicit schema + packet errors.
  - `python/zpe_iot/chemosense/contract.py`
  - `python/zpe_iot/chemosense/__init__.py`
- [x] **Action:** Unified CLI chemosense smoke flow onto shared contract primitive.
  - `python/zpe_iot/cli.py`
- [x] **Verify:** Contract + CLI module-path tests PASS.
  - `python/tests/test_chemosense_contract.py`
  - `python/tests/test_cli.py::test_module_execution_chemosense_smoke_json`

### Step C.7: Tightness + Provenance + DT Extension

- [x] **Action:** Removed superfluous multi-scan fusion parsing in hot path.
  - `python/zpe_iot/chemosense/taste/fusion_scheduler.py`
- [x] **Action:** Added chemosense perf profiling + report artifacts.
  - `validation/benchmarks/profile_chemosense.py`
  - `validation/results/perf_profile_chemosense_20260220T035037.json`
  - `docs/perf/chemosense_profile_20260220T035037.md`
- [x] **Action:** Added chemosense dataset adapters + provenance verifier.
  - `validation/datasets/build_chemosense_adapters.py`
  - `validation/datasets/verify_chemosense_provenance.py`
  - `validation/datasets/manifest_chemosense.json`
- [x] **Action:** Added chemosense DT-22..DT-25 and wired strict runner.
  - `validation/destruct_tests/dt22_modality_bit_collision.py`
  - `validation/destruct_tests/dt23_zlayer_decode_integrity.py`
  - `validation/destruct_tests/dt24_fusion_order_determinism.py`
  - `validation/destruct_tests/dt25_malformed_packet_resilience.py`
  - `validation/destruct_tests/run_all_dts.py`
- [x] **Verify:** Strict DT suite including new chemosense DTs is fully green.
  - `validation/results/dt_results_20260220T035518.json` (`PASS=25, FAIL=0, SKIPPED=0`)

### Step C.8: Chemosense RC Packaging (Deferred Publish)

- [x] **Action:** Added chemosense benchmark summary generation.
  - `validation/benchmarks/run_chemosense_benchmarks.py`
  - `validation/results/bench_summary_chemosense_20260220T035032.json`
- [x] **Action:** Added chemosense-specific RC bundle builder.
  - `scripts/build_chemosense_rc_bundle.py`
- [x] **Verify:** RC bundle generated locally.
  - `release/RC_CHEMOSENSE_20260220T035529/`

### Addendum C.1 Completion Gate

- [x] Contracted chemosense API/CLI semantics are unified and tested.
- [x] Hot-path tightness improvement is measured with artifact-backed latency gain.
- [x] Chemosense provenance manifest verifies at E1 floor for CS-01..CS-03.
- [x] Extended strict DT suite remains fully green with no mandatory skips.
- [x] RC bundle exists; public publishing remains deferred pending ratification.

### Step C.9: Supersession Note (2026-02-20)

- `[SUPERSEDED-2026-02-20 by rerun]` Prior RC path `release/RC_CHEMOSENSE_20260220T035529/`.
- Active RC path: `release/RC_CHEMOSENSE_20260220T035756/`.

## Addendum D (2026-02-20B): Touch + Mental Integration Sprint (PLANNED)

This addendum is append-only and records the next expansion lane.

### Step D.1: Touch Module Ingestion

- [ ] **Action:** Copy touch source modules from multimodality stream into:
  - `python/zpe_iot/chemosense/touch/`
- [ ] **Action:** Rewrite all `from source.*` imports to in-repo package imports.
- [ ] **Verify:** Touch encode/decode and z-layer helpers run without external path dependency.

### Step D.2: Mental Module Ingestion

- [ ] **Action:** Copy mental source modules into:
  - `python/zpe_iot/chemosense/mental/`
- [ ] **Action:** Preserve 8-direction + D6-12 profile semantics.
- [ ] **Verify:** RLE/raw mental pack/unpack paths remain deterministic.

### Step D.3: Cohesion and API Contract

- [ ] **Action:** Export touch and mental namespaces from `zpe_iot.chemosense`.
- [ ] **Action:** Add contract-level validators for touch and mental payload schemas.
- [ ] **Verify:** `python -m zpe_iot.cli ...` and `zpe-iot ...` paths are both operational.

### Step D.4: Fusion and Bit-Domain Hardening

- [ ] **Action:** Replace touch placeholder packet helper with canonical touch pack path.
- [ ] **Action:** Add contamination checks for type-bit separation:
  - smell `0x0200`
  - taste `0x0400`
  - touch `0x0800`
  - mental `0x0100`
- [ ] **Verify:** no cross-modality false decode under mixed streams.

### Step D.5: Validation and Gate Extension

- [ ] **Action:** Add touch/mental unit + property tests under `python/tests/`.
- [ ] **Action:** Extend strict DT suite with touch/mental invariants.
- [ ] **Action:** Re-run full quality stack:
```bash
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot/core"
cargo test
cargo clippy -- -D warnings
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot/python"
source .venv/bin/activate && pytest -q
cd "/Users/prinivenpillay/ZPE IoT/zpe-iot"
source python/.venv/bin/activate && python validation/destruct_tests/run_all_dts.py --strict-gates
```
- [ ] **Verify:** strict gate remains fully green with no mandatory SKIP/BLOCKED/FAIL.

### Addendum D Completion Gate

- [ ] Touch and mental modules fully local and import-clean.
- [ ] Touch placeholder path removed from chemosense smoke flow.
- [ ] Mixed-modality contamination tests pass.
- [ ] Python coverage threshold remains >=85%.
- [ ] Strict DT remains green after integration.
