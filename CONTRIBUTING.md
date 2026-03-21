<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# Contributing

<p>
  <img src=".github/assets/readme/section-bars/before-you-start.svg" alt="BEFORE YOU START" width="100%">
</p>

- Read `README.md`, `docs/ARCHITECTURE.md`, and `proofs/FINAL_STATUS.md`.
- Treat code, tests, and proof artifacts as authority over prose.
- Do not upgrade public-facing claims unless the same change set updates the cited evidence paths.

<p>
  <img src=".github/assets/readme/section-bars/environment-setup.svg" alt="ENVIRONMENT SETUP" width="100%">
</p>

```bash
cd /path/to/zpe-iot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e './python[dev]'
```

The repo scripts resolve the active interpreter dynamically. `.venv` is an example, not a hard-coded requirement.

<p>
  <img src=".github/assets/readme/section-bars/running-the-test-suite.svg" alt="RUNNING THE TEST SUITE" width="100%">
</p>

Run these before opening a PR:

```bash
cargo test --manifest-path core/Cargo.toml --release
cargo clippy --manifest-path core/Cargo.toml -- -D warnings
python -m pytest -q
python validation/destruct_tests/run_all_dts.py --strict-gates
bash scripts/release_preflight.sh
```

If you touch packaging or the native path, also run:

```bash
python -m build ./python
maturin build --manifest-path python/native/Cargo.toml --release
```

<p>
  <img src=".github/assets/readme/section-bars/our-standards.svg" alt="OUR STANDARDS" width="100%">
</p>

- Do not weaken strict DT gates, benchmark provenance rules, or dataset declarations.
- Do not silently widen the benchmark surface; `DS-11` stays blocked until the repo evidence changes.
- Keep `project_docs/` and older `release/RC_*` bundles as historical lineage.
- Do not add runtime coupling to `ZPE-IMC` unless the code truly requires it.
- Do not run publish steps without explicit owner ratification.
- Do not convert mixed evidence into a pass narrative.

<p>
  <img src=".github/assets/readme/section-bars/questions.svg" alt="QUESTIONS" width="100%">
</p>

Questions about contribution flow should route through `SUPPORT.md`. Security-sensitive reports go to `SECURITY.md`.

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>
