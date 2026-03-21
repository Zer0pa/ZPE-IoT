# Governance

Date: 2026-03-21
Model: owner-directed, evidence-first

## Decision Rules

| Rule | Meaning |
|---|---|
| Evidence outranks prose | Code, tests, manifests, and reproducible artifacts outrank documentation copy. |
| Mixed evidence is not a pass | Contradictory or partial results stay `INCONCLUSIVE` until closed by proof. |
| Current proof wins | March 21 authority artifacts outrank older March 9 release-blocked narratives. |
| Publication is owner-controlled | Public package publication, visibility changes, and outreach require explicit owner approval. |
| Family linkage is contractual | ZPE-IoT aligns to IMC by compatibility artifacts, not by runtime repo coupling. |

## Current Maintainer Scope

- repository structure and code
- validation and proof surfaces
- release-gate and install-path integrity
- doc truth and citation consistency

## Current Status Boundary

- private staging is allowed
- the managed release gate passes with only `D01_DEFERRED_PUBLISH` left deferred by policy
- public package publication is not yet claimed

## Current Non-Goals

- public-release theater before owner ratification
- benchmark inflation beyond the active E1 surface
- broad suite-coupling claims without current proof
