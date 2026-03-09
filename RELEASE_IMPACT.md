# Release Impact

## What This Phase Changes

- the repo now has a coherent front door
- proof, audit, and governance routing is explicit
- active family-linkage paths point at the current IMC repo location
- private GitHub staging can use the inner repo as the canonical boundary

## What This Phase Does Not Change

- no public release claim
- no PyPI publish
- no crates.io publish
- no blind-clone verification
- no new performance claim

## Current Blocking Impact

Because `C07_SBOM_RELEASE_MANIFEST` and `C10_CHEMOSENSE_CLI_SMOKE` are still unresolved in the last managed preflight, this phase improves repo integrity but does not establish release readiness.
