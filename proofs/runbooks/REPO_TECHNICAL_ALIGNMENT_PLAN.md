# Repo Technical Alignment Plan

Date: 2026-03-21
Repo: /Users/Zer0pa/ZPE/ZPE IoT/zpe-iot
Instruction Surface:
- /Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/proofs/runbooks/REPO_TECHNICAL_ALIGNMENT_EXECUTION_PROMPT.md
- /Users/Zer0pa/ZPE/ZPE IoT/zpe-iot/proofs/runbooks/REPO_TECHNICAL_EXECUTION_SUPPLEMENT.md

## Classification Hypothesis

Private-stage multi-surface codec repo:
- primary technical release unit: nested Python package in `python/` with CLI and optional native wheel
- sibling repo-local surfaces: Rust core crate in `core/`, PyO3 bridge in `python/native/`, C header/example in `c/`
- not one monolithic public release surface

## Execution Plan

1. Audit the real release boundary.
   - inspect package metadata, CLI entrypoints, native bridge, root scripts, workflows, and C surface
   - identify contradictions between repo truth and package/release truth

2. Align the primary Python release surface.
   - make dependency extras truthful for benchmark and observability sidecars
   - keep the base install narrow and technically honest
   - preserve native-wheel support without blurring it into the base Rust crate or C surface

3. Align release and verification tooling.
   - remove hardcoded root `.venv` assumptions where the tooling should follow the active interpreter/tool path
   - make preflight, SBOM/security, and checksum tooling runnable from a truthful operator environment
   - repair workflow logic only where the current repo layout or package truth is contradicted

4. Verify and falsify.
   - build the Python package
   - install the built wheel into a fresh venv and verify import, CLI, and native availability
   - run the relevant Python tests
   - run the release-preflight path
   - statically verify the release workflows
   - verify the repo-local C surface if it is still claimed

5. Write proof artifacts and the standard receipt.
   - record the final chosen architecture
   - list the evidence files only
   - leave board status as a recommendation, not an update
