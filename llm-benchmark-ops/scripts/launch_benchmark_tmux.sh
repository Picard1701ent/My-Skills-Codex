#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <run_id> <command...>"
  exit 1
fi

RUN_ID="$1"
shift

mkdir -p "result/logs/${RUN_ID}"
mkdir -p "result/summaries/${RUN_ID}"

SESSION="${RUN_ID}"
CMD="$*"

tmux new-session -d -s "${SESSION}" "${CMD} |& tee result/logs/${RUN_ID}/launcher.log"
echo "Started tmux session: ${SESSION}"
