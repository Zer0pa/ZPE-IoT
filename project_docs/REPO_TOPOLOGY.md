# Repository Topology

Status: Canonical as of 2026-02-19

## Canonical Paths

- Project root (memory/governance docs): `/Users/zer0pa-build/ZPE IoT`
- Canonical code repository: `/Users/zer0pa-build/ZPE IoT/zpe-iot`

## Roles

- Root repository (`/Users/zer0pa-build/ZPE IoT`): append-only PRD/runbook memory and orchestration governance.
- Code repository (`/Users/zer0pa-build/ZPE IoT/zpe-iot`): executable source, tests, benchmarks, release artifacts, and packaging logic.

## Sync and Export Policy

- Source of truth for memory docs remains root files.
- Release bundles use a synced snapshot in `/Users/zer0pa-build/ZPE IoT/zpe-iot/project_docs`.
- Snapshot is produced by:

```bash
cd '/Users/zer0pa-build/ZPE IoT/zpe-iot'
bash scripts/sync_memory_docs.sh
```

- Sync history is append-only at `project_docs/SYNC_HISTORY.md`.
- External publishing remains deferred until explicit user ratification.

## Engineer Quick Answer

Canonical product repo is: `/Users/zer0pa-build/ZPE IoT/zpe-iot`
