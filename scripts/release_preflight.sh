#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

PYTHON_BIN="${ZPE_IOT_PYTHON:-}"
if [[ -z "${PYTHON_BIN}" ]]; then
  for candidate in \
    "${ROOT_DIR}/python/.venv/bin/python" \
    "${ROOT_DIR}/.venv/bin/python"
  do
    if [[ -x "${candidate}" ]]; then
      PYTHON_BIN="${candidate}"
      break
    fi
  done
fi

if [[ -z "${PYTHON_BIN}" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python)"
  else
    echo "No usable Python interpreter found for release preflight" >&2
    exit 1
  fi
fi

export ZPE_IOT_COMET_OFFLINE=1
exec "${PYTHON_BIN}" scripts/release_preflight.py "$@"
