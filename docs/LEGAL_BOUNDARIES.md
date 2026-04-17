<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# Legal Boundaries

<p>
  <img src="../.github/assets/readme/section-bars/license-and-ip.svg" alt="LICENSE AND IP" width="100%">
</p>

| Field | Current truth |
|---|---|
| License | `LicenseRef-Zer0pa-SAL-6.2` |
| Citation surface | `../README.md` plus the March proof anchors cited there |
| Canonical repo URL | `https://github.com/Zer0pa/ZPE-IoT` |
| Current package status | Always-in-beta PyPI package is live; broader distribution guarantees remain owner-controlled |

This file is a compact boundary note. The legal source of truth remains `../LICENSE`.

<p>
  <img src="../.github/assets/readme/section-bars/unreleased.svg" alt="UNRELEASED" width="100%">
</p>

The repo does not currently establish:

- public crates.io availability
- multi-platform wheel closure beyond the cited local arm64 cold-install proof
- any production SLA beyond the cited repo artifacts

Broader release ceremony and outreach beyond the live PyPI package remain owner-controlled.

| Need | Go to |
|---|---|
| Legal source of truth | `../LICENSE` |
| Release decision boundary | `../validation/results/IOT_WAVE1_RELEASE_READINESS_REPORT.md` |
| Family compatibility pin | `family/IOT_COMPATIBILITY_VECTOR.json` |
| Family alignment note | `family/IOT_IMC_ALIGNMENT_REPORT.md` |

<p>
  <img src="../.github/assets/readme/section-bars/compatibility-note-for-parallel-tracks.svg" alt="COMPATIBILITY NOTE FOR PARALLEL TRACKS" width="100%">
</p>

The family relationship to ZPE-IMC is documentary and contractual:

- `docs/family/IOT_COMPATIBILITY_VECTOR.json` pins the IMC `wave1.0` contract
- ZPE-IoT does not claim runtime repo coupling to ZPE-IMC
- downstream consumers should pin to the family artifacts and current March proof anchors, not infer guarantees from internal implementation details

<p>
  <img src="../.github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>
