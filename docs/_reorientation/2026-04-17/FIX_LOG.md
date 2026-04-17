# Reorientation Fix Log — 2026-04-17

## Drift

- [README.md](../../../README.md) — updated the authority commit SHA, removed references to missing root policy files, and rewired the directory/support tables to files that actually exist in this repo.
- [docs/ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) — replaced the missing proof router and release bundle references with the live March readiness, benchmark, and release-manifest surfaces.
- [docs/LEGAL_BOUNDARIES.md](../../../docs/LEGAL_BOUNDARIES.md) — corrected the repo license from SAL-6.0 to SAL-6.2 and removed references to missing `CITATION.cff` / `RELEASING.md`.
- [validation/results/IOT_WAVE1_RELEASE_READINESS_REPORT.md](../../../validation/results/IOT_WAVE1_RELEASE_READINESS_REPORT.md) — rewrote the stale February-era path ledger into a current March authority summary that points to files still present in the repo.
- [docs/family/IOT_IMC_ALIGNMENT_REPORT.md](../../../docs/family/IOT_IMC_ALIGNMENT_REPORT.md) — removed the missing `proofs/FINAL_STATUS.md` reference.

## Clarity

- [README.md](../../../README.md) — replaced defensive repo-state wording with direct product language and a concrete install/proof posture.
- [docs/ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) — clarified the proof router and release evidence surface instead of pointing at absent proof index files.
- [validation/results/IOT_WAVE1_RELEASE_READINESS_REPORT.md](../../../validation/results/IOT_WAVE1_RELEASE_READINESS_REPORT.md) — made the report explicit about what is historical lineage versus current authority.

## Consistency

- [README.md](../../../README.md), [docs/ARCHITECTURE.md](../../../docs/ARCHITECTURE.md), and [docs/LEGAL_BOUNDARIES.md](../../../docs/LEGAL_BOUNDARIES.md) — aligned repo-facing license language to the current SAL v6.2 root license surface.
- [README.md](../../../README.md), [docs/market_surface.json](../../../docs/market_surface.json), and [docs/family/IOT_RELEASE_NOTE_FOR_COORDINATION.md](../../../docs/family/IOT_RELEASE_NOTE_FOR_COORDINATION.md) — aligned package/publication posture to the live PyPI package instead of older private-stage framing.
- [validation/runbooks/RUNBOOK_IOT_WAVE1_MASTER.md](../../../validation/runbooks/RUNBOOK_IOT_WAVE1_MASTER.md) and [validation/runbooks/RUNBOOK_IOT_WAVE1_PHASE_0.md](../../../validation/runbooks/RUNBOOK_IOT_WAVE1_PHASE_0.md) through [validation/runbooks/RUNBOOK_IOT_WAVE1_PHASE_6.md](../../../validation/runbooks/RUNBOOK_IOT_WAVE1_PHASE_6.md) — marked the wave runbooks as historical operator lineage so they no longer conflict with the March authority surface.

## Framing

- [README.md](../../../README.md) — rewrote portfolio references so ZPE-IoT speaks as one independent encoding product, not as a shared platform story.
- [docs/market_surface.json](../../../docs/market_surface.json) — changed the repo role and family-position framing from `product_candidate` / umbrella language to an independent encoding product with documentary IMC alignment.
- [docs/family/IOT_IMC_ALIGNMENT_REPORT.md](../../../docs/family/IOT_IMC_ALIGNMENT_REPORT.md) — clarified that IMC is a coordination contract, not a shared runtime substrate.

## Beta posture

- [README.md](../../../README.md) — replaced `private-stage` with the always-in-beta posture: useful now, improving continuously.
- [docs/LEGAL_BOUNDARIES.md](../../../docs/LEGAL_BOUNDARIES.md) — replaced negative package-status wording with a live-package / owner-controlled-boundary statement.
- [docs/family/IOT_RELEASE_NOTE_FOR_COORDINATION.md](../../../docs/family/IOT_RELEASE_NOTE_FOR_COORDINATION.md) — rewrote deferred-publication notes so they describe owner-controlled expansion beyond the current live package, not a repo that is "not yet ready."

## Primitive scope

- [README.md](../../../README.md) — kept the product-specific eight-direction codec description and removed portfolio-scale framing.
- [docs/market_surface.json](../../../docs/market_surface.json) — narrowed the technical wedge to this repo's eight-direction sensor codec instead of implying a portfolio-wide substrate.
- [docs/_reorientation/2026-04-17/NOVELTY_CARD.md](./NOVELTY_CARD.md) — cited the actual Compass-8 implementation lines in `python/zpe_iot/codec.py` and `core/src/quantise.rs`.

## Honest limits

- [README.md](../../../README.md) — kept the DS-12 competitor win, DS-11 blocker, bounded-lossy boundary, and cold-install scope visible while removing apologetic stage language.
- [validation/results/IOT_WAVE1_RELEASE_READINESS_REPORT.md](../../../validation/results/IOT_WAVE1_RELEASE_READINESS_REPORT.md) — surfaced the live PyPI package, the broader distribution limits, and the DS-11 source blocker directly in the authority report.
- [docs/LEGAL_BOUNDARIES.md](../../../docs/LEGAL_BOUNDARIES.md) — removed the false "no public PyPI availability" claim and left only the limits that are still real.
