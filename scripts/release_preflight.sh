#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

export ZPE_IOT_COMET_OFFLINE=1
exec .venv/bin/python scripts/release_preflight.py "$@"
