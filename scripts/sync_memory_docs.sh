#!/usr/bin/env bash
set -euo pipefail

CODE_REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "${CODE_REPO_DIR}/.." && pwd)"
DEST_DIR="${CODE_REPO_DIR}/project_docs"
HISTORY_FILE="${DEST_DIR}/SYNC_HISTORY.md"

DOCS=(
  "PRD_06_ENTERPRISE_EXECUTION_v1.0.md"
  "RUNBOOK_00_MASTER.md"
  "RUNBOOK_01_CORE_CODEC.md"
  "RUNBOOK_02_FALSIFICATION.md"
  "RUNBOOK_03_SDK_PACKAGE.md"
  "RUNBOOK_04_BENCHMARKS.md"
  "RUNBOOK_05_LAUNCH.md"
  "ZPE_IOT_SENSOR_COMPRESSION_SDK_PRD_v1.0.md"
  "REPO_TOPOLOGY.md"
)

mkdir -p "${DEST_DIR}"

if [[ ! -f "${HISTORY_FILE}" ]]; then
  cat > "${HISTORY_FILE}" <<'HIST'
# Memory Sync History

| timestamp_utc | source | destination | sha256 |
|---|---|---|---|
HIST
fi

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

for doc in "${DOCS[@]}"; do
  src="${ROOT_DIR}/${doc}"
  dst="${DEST_DIR}/${doc}"

  if [[ ! -f "${src}" ]]; then
    echo "[WARN] missing source doc: ${src}" >&2
    continue
  fi

  cp "${src}" "${dst}"
  sha="$(shasum -a 256 "${dst}" | awk '{print $1}')"
  printf '| %s | `%s` | `%s` | `%s` |\n' "${ts}" "${src}" "${dst}" "${sha}" >> "${HISTORY_FILE}"
done

echo "Synced memory docs into ${DEST_DIR}"
