# Docs Falsification Report

Date: 2026-03-21
Repo: `/Users/Zer0pa/ZPE/ZPE IoT/zpe-iot`
Pushed commit: `2538cfe8b83a87b2c01ff4c643fbb4325017b368`

## Unsupported Claims Removed Or Downgraded

- Removed the March 9 blocked-preflight narrative from `README.md`, `proofs/FINAL_STATUS.md`, `proofs/PROOF_INDEX.md`, `AUDITOR_PLAYBOOK.md`, `PUBLIC_AUDIT_LIMITS.md`, `RELEASING.md`, `ROADMAP.md`, and `docs/README.md`.
- Removed the stale `4.37x` and `6/8` benchmark promotion from the front-door and replaced it with the March 21 E1 authority surface (`10/11`, `17.163613932777356x`).
- Retired `C07_SBOM_RELEASE_MANIFEST` and `C10_CHEMOSENSE_CLI_SMOKE` as current blockers; kept only the truthful `D01_DEFERRED_PUBLISH` boundary.
- Kept acquisition truth at private repo checkout or owner-shared wheel only; no public PyPI or crates.io install claim was introduced.

## Path And Render Issues Found

- The repo did not contain the IMC readme asset system. `.github/assets/readme/` was copied in so the root README and supporting docs can render the same masthead and section-bar system on GitHub.
- `docs/README.md` initially under-routed the new FAQ, support, and legal-boundary surfaces. That routing was added.
- Local asset-path verification across the touched docs returned `ALL_ASSET_PATHS_OK`.
- Live private GitHub render was verified through authenticated `gh api` HTML rendering for:
  - root `README.md`
  - `docs/README.md`
  - `docs/BENCHMARKS.md`
  - `docs/DOC_REGISTRY.md`

## Remaining Owner Inputs

- None for the documentation pass itself.
- Public publication, tags, and outreach remain owner-ratified actions by policy, but they are not blockers to the current docs truth surface.

## Live-Vs-Local Drift Found And Resolved

- `origin/main` advanced by one CI-only commit during the pass (`5d924b05f506765873211cb8b235cff03d91a782`, `ci: add auto-add-to-project workflow`).
- The docs commit was rebased over that remote commit with `git pull --rebase --autostash origin main` and pushed successfully.
- The pushed branch is now synchronized at `2538cfe8b83a87b2c01ff4c643fbb4325017b368`.
- Direct browser render verification through Playwright failed because the browser session was not authenticated to the private GitHub repo. Render verification was completed through authenticated `gh api` instead.
