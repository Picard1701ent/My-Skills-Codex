#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="${SCRIPT_DIR}/pdf_corpus_scan.py"

try_system_python() {
  if command -v python3 >/dev/null 2>&1; then
    if python3 -c "import pypdf" >/dev/null 2>&1; then
      exec python3 "${PY_SCRIPT}" "$@"
    fi
  fi
  return 1
}

try_conda_multi_agent() {
  local conda="/home/ubuntu/.codex/miniconda3/bin/conda"
  if [ -x "${conda}" ]; then
    exec "${conda}" run -n multi-agent python "${PY_SCRIPT}" "$@"
  fi
  return 1
}

if try_system_python "$@"; then
  exit 0
fi

if try_conda_multi_agent "$@"; then
  exit 0
fi

echo "[error] Could not find a usable Python with PDF dependencies." >&2
echo "Install pypdf (e.g., in conda env 'multi-agent') and retry." >&2
exit 2

