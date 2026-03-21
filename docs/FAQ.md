<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# FAQ

If your question is not answered here, start with [SUPPORT.md](SUPPORT.md).

<p>
  <img src="../.github/assets/readme/section-bars/architecture-and-theory.svg" alt="ARCHITECTURE AND THEORY" width="100%">
</p>

**What is ZPE-IoT?**

ZPE-IoT is the Zero-Point Encoding workstream for 1D IoT sensor compression. It uses a Rust codec kernel, a nested Python distribution, and a repo-local native wheel build surface to encode time-series into deterministic packet bytes.

**Is this repo public or published to package indexes?**

No. The repo is still a private-stage GitHub repo. Public PyPI and crates.io publication remain deferred by policy.

**Is ZPE-IoT lossless?**

No. ZPE-IoT is a bounded-lossy codec. It is not suitable for strict lossless reconstruction requirements.

**How does ZPE-IoT relate to ZPE-IMC?**

The relationship is contractual, not runtime-coupled. ZPE-IoT pins to the IMC `wave1.0` compatibility artifacts in `docs/family/`, but the repo does not import ZPE-IMC as a runtime dependency.

<p>
  <img src="../.github/assets/readme/section-bars/setup-and-verification.svg" alt="SETUP AND VERIFICATION" width="100%">
</p>

**How do I install the current repo truthfully?**

Use a private repo checkout or an owner-shared wheel:

```bash
git clone https://github.com/Zer0pa/ZPE-IoT zpe-iot
cd zpe-iot
python -m pip install -e './python[dev]'
```

The March 21 local arm64 macOS wheel path is also evidenced, but it is not a public package-index claim.

**What does the current repo actually prove?**

The current repo proves the managed preflight, strict DT, native cold-install smoke, and the promoted E1 benchmark surface described in `../proofs/FINAL_STATUS.md`. Use that file for the exact current values instead of treating this FAQ as the status ledger.

**Where do I verify the current gate quickly?**

Start with:

- `../proofs/FINAL_STATUS.md`
- `../proofs/PROOF_INDEX.md`
- `../AUDITOR_PLAYBOOK.md`

<p>
  <img src="../.github/assets/readme/section-bars/integration-and-downstream-use.svg" alt="INTEGRATION AND DOWNSTREAM USE" width="100%">
</p>

**Does ZPE-IoT beat general-purpose compressors everywhere?**

No. The promoted benchmark surface still contains a competitor win and a blocked dataset. Use `BENCHMARKS.md` for the exact current scoreline instead of treating this FAQ as the live benchmark ledger.

**Is the native path available by default for every platform?**

No public multi-platform claim is made. The currently evidenced native install path is the local arm64 macOS wheel. The workflow for broader wheel targets exists, but that is not the same as a published multi-platform release.

**What is the chemosense surface here?**

The Python package includes `zpe_iot.chemosense`, with smoke, contract, and benchmark artifacts in the repo. It is part of the staged engineering surface, but it does not replace the sensor benchmark authority surface in `BENCHMARKS.md`.

<p>
  <img src="../.github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>
