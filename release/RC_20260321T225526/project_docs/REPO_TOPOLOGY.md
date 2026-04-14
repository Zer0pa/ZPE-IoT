# Repository Topology

Status: Canonical as of 2026-02-19

## Canonical Paths

- Project root (memory/governance docs): `<BUILD_HOME>/ZPE IoT`
- Canonical code repository: `<REPO_ROOT>`

## Roles

- Root repository (`<BUILD_HOME>/ZPE IoT`): append-only PRD/runbook memory and orchestration governance.
- Code repository (`<REPO_ROOT>`): executable source, tests, benchmarks, release artifacts, and packaging logic.

## Sync and Export Policy

- Source of truth for memory docs remains root files.
- Release bundles use a synced snapshot in `<REPO_ROOT>/project_docs`.
- Snapshot is produced by:

```bash
cd '<REPO_ROOT>'
bash scripts/sync_memory_docs.sh
```

- Sync history is append-only at `project_docs/SYNC_HISTORY.md`.
- External publishing remains deferred until explicit user ratification.

## Engineer Quick Answer

Canonical product repo is: `<REPO_ROOT>`
