<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# Legal Boundaries

<p>
  <img src="../.github/assets/readme/section-bars/license-and-ip.svg" alt="LICENSE AND IP" width="100%">
</p>

| Field | Current truth |
|---|---|
| License | `MIT` |
| Citation surface | `../CITATION.cff` |
| Canonical repo URL | `https://github.com/Zer0pa/ZPE-IoT` |
| Current package status | Private-stage repo and locally built artifacts only |

This file is a compact boundary note. The legal source of truth remains `../LICENSE`.

<p>
  <img src="../.github/assets/readme/section-bars/unreleased.svg" alt="UNRELEASED" width="100%">
</p>

The repo does not currently establish:

- public PyPI availability
- public crates.io availability
- a public multi-platform wheel release
- any production SLA beyond the cited repo artifacts

Public publication and outreach remain owner-controlled.

<p>
  <img src="../.github/assets/readme/section-bars/compatibility-note-for-parallel-tracks.svg" alt="COMPATIBILITY NOTE FOR PARALLEL TRACKS" width="100%">
</p>

The family relationship to ZPE-IMC is documentary and contractual:

- `docs/family/IOT_COMPATIBILITY_VECTOR.json` pins the IMC `wave1.0` contract
- ZPE-IoT does not claim runtime repo coupling to ZPE-IMC
- downstream consumers should pin to the family artifacts, not infer guarantees from internal implementation details
