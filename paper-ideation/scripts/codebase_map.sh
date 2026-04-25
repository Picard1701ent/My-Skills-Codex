#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="${SCRIPT_DIR}/codebase_map.py"

if command -v python3 >/dev/null 2>&1; then
  exec python3 "${PY_SCRIPT}" "$@"
fi

echo "[error] python3 not found" >&2
exit 2

