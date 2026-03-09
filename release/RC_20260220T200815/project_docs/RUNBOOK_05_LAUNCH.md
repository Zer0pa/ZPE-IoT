# RUNBOOK_05_LAUNCH.md — Phase 5: Launch & Sell

**STOP.** Have you read `RUNBOOK_00_MASTER.md`? If no, read it NOW.
**Is Phase 4 marked `PASSED` in the Phase Gates table?** If no, go back to `RUNBOOK_04`.

---

## Phase 5 Objective

Ship the SDK publicly, create sales materials, identify target customers, run outreach, and close the first paying customer or active pilot. This is where engineering becomes revenue.

**Input:** Validated, packaged, benchmarked SDK from Phases 1-4
**Output:** Public SDK + first paying customer or 3 active pilots
**Gating:** Revenue event OR 3 pilots with named companies
**Duration:** ~20 days

---

## Step 0: Public Release

### Step 0.1: Final Pre-Release Audit

- [x] **Action:** Before publishing, verify:
1. `python validation/destruct_tests/run_all_dts.py` — ALL P0+P1 green
2. `pip install zpe-iot` works from wheel
3. `examples/python/quickstart.py` runs
4. `docs/API.md` is current
5. `docs/BENCHMARKS.md` has real numbers
6. No hardcoded paths, no secrets, no debug prints in production code
7. LICENSE file (MIT) present
8. README.md present and accurate

### Step 0.2: Publish to PyPI

- [x] **Action:** DEFERRED (missing PyPI API token in this environment).
```bash
cd python
python -m build
twine upload dist/*
```
- [x] **Verify:** DEFERRED (cannot verify PyPI install without publish credentials).

**NOTE:** Requires PyPI API token. If unavailable, mark `DEFERRED`.

### Step 0.3: Publish to crates.io

- [x] **Action:** DEFERRED (missing crates.io token in this environment).
```bash
cd core
cargo publish
```
- [x] **Verify:** DEFERRED (cannot verify crates.io availability without publish credentials).

**NOTE:** Requires crates.io token. If unavailable, mark `DEFERRED`.

### Step 0.4: Push to GitHub

- [x] **Action:** DEFERRED (missing GitHub auth/remote access in this environment).
```bash
git remote add origin git@github.com:zer0pa/zpe-iot.git
git push -u origin main
```
- [x] **Verify:** DEFERRED (cannot verify remote accessibility without push access).

---

## Step 1: Sales Materials

### Step 1.1: README as Landing Page

- [x] **Action:** The GitHub README IS the landing page. It must contain:

```markdown
# zpe-iot — Compress Sensor Data 5-10x on Any MCU

**GPU-free. Deterministic. 4 KB RAM. Faster than zstd on time-series.**

## Quick Start (Python)
[10-line example]

## Quick Start (Rust)
[5-line example]

## Benchmarks
[Summary table from Phase 4 — CR comparison chart embedded]

## Supported Sensor Types
[Table of presets]

## Why Not Just Use zstd/LZ4?
[2-sentence answer: "General compressors get 2-3x on sensor data.
zpe-iot gets 5-10x because it understands signal structure."]

## Installation
pip install zpe-iot
cargo add zpe-iot

## License
MIT (free for evaluation and small deployments)
Commercial license for >100 devices: contact sales@zer0pa.com

## ROI Calculator
[Link to BENCHMARKS.md#roi-calculator]
```

### Step 1.2: One-Page Sales PDF

- [x] **Action:** Create `docs/ZPE_IOT_SALES_BRIEF.md` (markdown, convertible to PDF):

```markdown
# ZPE-IoT: Cut Your IoT Data Costs by 80%

## The Problem
Every IoT device transmitting over cellular pays $0.50-$2.00/MB.
At 10,000 devices × 1 MB/day, that's $1.8M-$7.3M/year in data costs alone.

## The Solution
ZPE-IoT compresses sensor data 5-10x using geometric encoding.
No GPU. No cloud. Runs on ESP32, STM32, nRF, RISC-V.

## Proven Results
[Benchmark table from Phase 4]

## How It Works
1. pip install zpe-iot (or link C library to your firmware)
2. compressed = zpe_iot.encode(sensor_data, preset="vibration")
3. Send compressed bytes instead of raw data
4. Receiver: zpe_iot.decode(compressed)

## Pricing
| Tier | Price | Includes |
| Free | $0 | Core SDK, 3 presets, MIT license |
| Pro | $25K-100K/year | All presets, tuning, support |
| Embedded | Per-unit royalty | Certified library, integration support |

## Next Step
pip install zpe-iot
Try it on your data in 5 minutes.
```

### Step 1.3: Savings Calculator Script

- [x] **Action:** Create `scripts/savings_calculator.py`:

Interactive CLI:
```
How many devices? 10000
Average data per device per day (KB)? 500
Cellular cost per MB ($)? 1.00
---
Current annual cost: $1,825,000
With zpe-iot (5x compression): $365,000
Annual savings: $1,460,000
ZPE-IoT Pro license: $50,000/year
Net ROI: 29x
```

---

## Step 2: Customer Identification

### Step 2.1: Build Target List

- [x] **Action:** Identify 10 companies that match the Target Customer Profile (PRD §13.1).

Research criteria:
- IoT/industrial company, 10-500 employees
- Sends sensor data over cellular (LTE-M, NB-IoT, satellite)
- Publicly discusses data costs, bandwidth, or battery life as challenges
- Has engineering blog / GitHub presence (technical buyer accessible)

Sources to search:
- Crunchbase: "IoT" + "sensor" + recent funding
- HN "Who's Hiring": IoT companies
- AWS IoT / Azure IoT partner directories
- LinkedIn: "IoT CTO" / "embedded engineering lead"
- Reddit r/embedded, r/IOT discussions about data costs

Record in `docs/TARGET_CUSTOMERS.md`:
```markdown
| # | Company | What They Do | Signal Type | Est. Devices | Contact Strategy |
|---|---------|-------------|-------------|-------------|-----------------|
| 1 | ... | ... | ... | ... | ... |
```

### Step 2.2: Validate Problem Exists

- [x] **Action:** For top 5 companies, find evidence they have the data cost problem:
- Blog posts about cellular costs
- Job postings mentioning "data optimisation" or "bandwidth reduction"
- Conference talks about edge processing
- GitHub repos showing data compression attempts
- Forum posts asking about sensor data compression

Document evidence in `docs/TARGET_CUSTOMERS.md`.

---

## Step 3: Outreach

### Step 3.1: Prepare Demo Script

- [x] **Action:** Create a reusable demo script that:
1. Takes a company's sample data (CSV/JSON/binary)
2. Runs zpe-iot vs zstd/LZ4 comparison
3. Produces a 1-page report with their specific savings numbers
4. Takes < 5 minutes to run

Script: `scripts/customer_demo.py <input_file> [--preset PRESET]`

### Step 3.2: Write Outreach Template

- [x] **Action:** Create `docs/OUTREACH_TEMPLATE.md`:

```
Subject: Cut [COMPANY]'s cellular data costs by 80%?

Hi [NAME],

I noticed [COMPANY] deploys [N] [SENSOR_TYPE] sensors over [NETWORK].
At $[COST]/MB, that's roughly $[ANNUAL] in data transport alone.

I built an open-source compression library (zpe-iot) that typically
gets 5-10x compression on [SENSOR_TYPE] data — compared to 2-3x
from zstd/LZ4. It runs on [MCU] with 4KB RAM, no GPU needed.

Here's a benchmark on public [SENSOR_TYPE] data: [LINK]

Would you be open to a 5-minute test on your actual sensor data?
I'll send you the report — no cost, no commitment.

Best,
[NAME]

P.S. pip install zpe-iot — try it yourself: [GITHUB_LINK]
```

### Step 3.3: Send Outreach

- [ ] **Action:** Send personalised outreach to 10 targets.
- [ ] **Track:** Record responses in `docs/TARGET_CUSTOMERS.md`.

### Step 3.4: Run Pilot Demos

- [ ] **Action:** For every company that responds:
1. Get sample sensor data (CSV or description of signal type)
2. Run `scripts/customer_demo.py` on their data
3. Send 1-page results with savings estimate
4. Offer free Pro trial (30 days)

- [ ] **Track:** Pilot status in `docs/TARGET_CUSTOMERS.md`.

---

## Step 4: Community Launch

### Step 4.1: Hacker News Post

- [ ] **Action:** Submit Show HN post:
```
Show HN: ZPE-IoT – 5-10x sensor data compression on ESP32/STM32 (4KB RAM, no GPU)

Built this because IoT companies pay $0.50-$2.00/MB for cellular data.
General compressors (zstd, LZ4) get 2-3x on sensor time-series.
ZPE-IoT gets 5-10x by encoding signal direction geometrically.

Benchmarks: [LINK]
GitHub: [LINK]
pip install zpe-iot

Runs on anything with a CPU. No training, no GPU, no cloud dependency.
Deterministic: same input always produces same output. FDA-certifiable.

Feedback welcome — especially from embedded/IoT engineers.
```

### Step 4.2: Reddit Posts

- [ ] **Action:** Post to r/embedded, r/IOT, r/rust with relevant framing.

### Step 4.3: Respond to Community

- [ ] **Action:** Monitor and respond to all comments/issues for 2 weeks post-launch.
- GitHub Issues: respond within 24h
- HN comments: respond within 4h on launch day

---

## Phase 5 Completion Gate

- [ ] SDK published to PyPI (or available via GitHub pip install)
- [ ] SDK published to crates.io (or available via GitHub)
- [x] README serves as landing page
- [x] Sales brief created
- [x] 10 target companies identified with evidence of data cost problem
- [ ] 10 outreach messages sent
- [ ] At least 3 demo/pilot conversations started
- [ ] OR: first paying customer closed

**Revenue milestone tracking:**
- [ ] M1: First pilot (company compressing their data with zpe-iot)
- [ ] M2: First revenue (Pro license or consulting)
- [ ] M3: 3 paying customers
- [ ] M4: $10K MRR

- [x] Phase Gates table in RUNBOOK_00 updated
- [ ] Git commit: `[PHASE-5] Launch complete`

---

## Addendum A (2026-02-14): Controlled Launch Deferral (ACTIVE)

This addendum keeps prior launch steps as historical plan but imposes stricter pre-publish controls.

### Step A.0: Publish Deferral Lock

- [x] **Action:** Keep Step 0.2, 0.3, and 0.4 deferred until hardening gates are satisfied and user ratifies release.
- [x] **Verify:** No external publish command is executed before `H-GATE-LAUNCH` is PASS.

### Step A.1: Hard Launch Gate (H-GATE-LAUNCH)

Before any public release actions:

- [x] Strict DT run completed with mandatory `SKIPPED=0`
- [x] DS-01..DS-08 provenance class >= `real_public`
- [x] PT-6 status is `FINAL` (not `PROVISIONAL`)
- [x] `docs/BENCHMARKS.md` labels evidence class for every headline claim
- [x] `scripts/customer_demo.py` performs side-by-side comparison vs zstd/LZ4/zlib and outputs a single report artifact
- [ ] User gives explicit "publish now" approval

### Step A.2: Sales Truthfulness Guardrail

- [x] **Action:** Outreach and sales assets must reference evidence class (`E1` or `E2`) for claims.
- [x] **Action:** If data is proxy (`E0`), claims must be framed as exploratory and not superiority claims.
- [x] **Verify:** `docs/ZPE_IOT_SALES_BRIEF.md` and `docs/OUTREACH_TEMPLATE.md` contain compliant wording.

### Step A.3: Pilot Priority Before Public Blast

- [ ] **Action:** Prioritize private pilot demos with real customer data before HN/Reddit launch.
- [ ] **Track:** For each pilot, log:
  - data source and consent status
  - compression/fidelity results
  - estimated cost savings
  - blockers to conversion
- [ ] **Verify:** At least 3 pilot-ready reports exist before community launch posts.

### Addendum A Completion Gate

- [ ] H-GATE-LAUNCH is PASS
- [x] Sales/outreach messaging matches evidence class
- [ ] Pilot evidence artifacts exist and are linked in `docs/TARGET_CUSTOMERS.md`
- [ ] User ratifies public launch execution

---

## Addendum B (2026-02-14B): Pre-Publish Truth Freeze (ACTIVE)

This addendum preserves all prior launch steps and adds a stricter local freeze.

### Step B.1: Local Closure Dependency

- [ ] **Action:** Treat RUNBOOK_00 §11 (`DCL-01..DCL-07`) as hard prerequisite for any launch unfreeze.
- [ ] **Verify:** H-GATE-LAUNCH cannot be marked PASS until §11 is complete.

### Step B.2: Claim Freeze Rule

- [ ] **Action:** Freeze sales/community claim language to active E1 metrics until real customer (`E2`) benchmark totals are non-zero.
- [ ] **Action:** Disallow unqualified "FINAL" messaging for tiers with zero dataset count.
- [ ] **Verify:** README, sales brief, outreach template, and launch drafts are label-consistent.

### Step B.3: Publish Approval Protocol

- [ ] **Action:** Require explicit user confirmation phrase: `publish now`.
- [ ] **Action:** Log timestamp and command transcript for any release action after approval.
- [ ] **Verify:** No accidental publish command is run before approval event is recorded.

### Addendum B Completion Gate

- [ ] RUNBOOK_00 §11 complete
- [ ] Evidence-tier claim freeze satisfied across public-facing assets
- [ ] Explicit user publish approval logged

---

**End of RUNBOOK_05. This is the final phase. After this: iterate, sell, grow.**

### Addendum B Execution Update (2026-02-19E)

- [x] **Step B.1:** Local closure dependency satisfied
  - RUNBOOK_00 §11 and §12 enterprise execution updates completed.
  - Strict DT confirmation: `zpe-iot/validation/results/dt_results_20260219T030940.json`.
- [x] **Step B.2:** Claim freeze rule satisfied
  - Label-consistent assets refreshed:
    - `zpe-iot/README.md`
    - `zpe-iot/docs/BENCHMARKS.md`
    - `zpe-iot/docs/ZPE_IOT_SALES_BRIEF.md`
    - `zpe-iot/docs/OUTREACH_TEMPLATE.md`
  - Zero-tier behavior remains `NOT_AVAILABLE` for E2 split.
- [x] **Step B.3 (local portion):** Publish approval protocol enforced locally
  - No external publish command executed in this cycle.
  - RC bundle assembled locally: `zpe-iot/release/RC_20260219T031240/`.

### Addendum B Completion Gate Refresh (2026-02-19E)

- [x] RUNBOOK_00 §11 complete
- [x] Evidence-tier claim freeze satisfied across public-facing assets
- [ ] Explicit user publish approval logged
