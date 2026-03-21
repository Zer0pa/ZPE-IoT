<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# FAQ

If your question is not answered here, see `SUPPORT.md`.

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
git clone https://github.com/Zer0pa/ZPE-IoT
cd zpe-iot
python -m pip install -e './python[dev]'
```

The March 21 local arm64 macOS wheel path is also evidenced, but it is not a public package-index claim.

**What does the current repo actually prove?**

As of 2026-03-21, the repo proves a passing managed preflight (`17 PASS / 0 FAIL / 1 DEFERRED`), a passing strict DT surface (`27/27`), a local arm64 wheel cold-install smoke pass, and an active E1 benchmark surface of `10/11` wins at `17.16x` mean CR.

**Where do I verify the current gate quickly?**

Start with:

- `../proofs/FINAL_STATUS.md`
- `../proofs/PROOF_INDEX.md`
- `../AUDITOR_PLAYBOOK.md`

<p>
  <img src="../.github/assets/readme/section-bars/integration-and-downstream-use.svg" alt="INTEGRATION AND DOWNSTREAM USE" width="100%">
</p>

**Does ZPE-IoT beat general-purpose compressors everywhere?**

No. The current E1 surface is `10/11` wins. `DS-12` remains a competitor win and `DS-11` remains explicitly blocked from the active E1 surface.

**Is the native path available by default for every platform?**

No public multi-platform claim is made. The currently evidenced native install path is the local arm64 macOS wheel. The workflow for broader wheel targets exists, but that is not the same as a published multi-platform release.

**What is the chemosense surface here?**

The Python package includes `zpe_iot.chemosense`, with smoke, contract, and benchmark artifacts in the repo. It is part of the staged engineering surface, but it does not replace the sensor benchmark authority surface in `BENCHMARKS.md`.
