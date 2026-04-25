---
name: llm-benchmark-ops
description: Run and monitor LLM benchmark matrices with a smoke-to-full workflow. Use for multi-model, multi-benchmark execution with tmux/nohup, structured logs, and resumable operations.
---

# LLM Benchmark Ops

## Overview
Use this skill to execute benchmark matrices safely: smoke test first, then full run.
It emphasizes runtime reliability, monitoring, and repeatable command structure.

## When To Use
Use this skill when the user asks to:
- run multiple models across multiple benchmarks
- launch long jobs in background
- track token/API/cost metrics while running
- resume or retry failed benchmark subsets

## Standard Workflow
1. **Preflight checks**
   - Env exists and imports pass.
   - Dataset paths available.
   - API connectivity test succeeds.
2. **Smoke run**
   - Run small subset (`sample_size`) for each benchmark/model.
   - Confirm logs + summaries are generated.
3. **Full run launch**
   - Start detached execution (prefer tmux for long sessions).
   - Save `run_id`, session name, and launcher log path.
4. **Live monitoring**
   - Tail current benchmark log.
   - Detect stalls via unchanged batch index / timestamp.
5. **Post-run verification**
   - Confirm all expected summaries exist.
   - Confirm `master_summary.json` is generated.
6. **Retry failed units only**
   - Re-run by model + benchmark, not whole matrix.

## Command Conventions
- Smoke mode: use sample subset flags per benchmark script.
- Full mode: run with full dataset and persistent logging.
- Store run artifacts under `result/logs/<run_id>` and `result/summaries/<run_id>`.

Detailed command patterns are in `references/command-cookbook.md`.

## Failure Recovery Rules
- If one benchmark fails, continue remaining matrix items.
- Record exit code and stderr excerpt in run summary.
- Retry failed item once after dependency/config check.

## Fast Start
- Use `scripts/launch_benchmark_tmux.sh` for detached execution.
- Use `references/troubleshooting.md` for common stuck/failure patterns.
