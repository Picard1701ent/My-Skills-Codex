---
name: long-run-experiment-recovery
description: Recover, resume, and triage long-running experiment jobs with minimal wasted work. Use when detached runs stall, fail mid-pipeline, lose terminal visibility, or must be resumed safely from existing logs, progress files, summaries, or checkpoints.
---

# Long-Run Experiment Recovery

## Overview

Use this skill to recover a long experiment from artifact-backed state instead of guessing from terminal output.
Prefer resuming from the latest successful stage or checkpoint over restarting the whole run.

## Recovery Workflow

1. Identify the run id, launcher mode, and expected stages.
2. Use file-backed truth first:
   - current log files
   - progress files
   - stage summaries
   - master summary
   - checkpoint directories
3. Classify the state before acting:
   - never started
   - still running
   - completed stage but orchestration failed later
   - hard failure with reusable outputs
   - hard failure with unusable outputs
4. Resume from the narrowest safe boundary:
   - current stage if it has explicit resume support
   - next stage if the prior stage already wrote a successful summary
   - selected checkpoint if training completed but wrapper logic failed
5. Record the recovery decision and why a full restart was avoided or required.

## Recovery Rules

- Trust `master_summary.json` and stage summaries over shell history.
- Treat a completed stage summary plus valid outputs as reusable, even if the parent orchestrator failed later.
- Do not rerun upstream expensive stages when downstream state proves they already succeeded.
- If progress files exist without final summary, inspect whether the stage supports resume before restarting.
- If a run is blocked by a deterministic environment issue, fix the environment first and then resume from the latest reusable point.

## Triage Heuristics

- Cold start vs hard failure:
  - cold start usually shows live process state with sparse logs and no terminal error
  - hard failure usually writes an incident, traceback, or non-zero stage summary
- Detached session unavailable:
  - fall back to log files and process inspection
  - do not assume the job is dead because `tmux` visibility is lost
- Partial training output:
  - reuse checkpoint directories with trainer state when supported
  - avoid deleting partial checkpoints unless corruption is confirmed
- Partial data generation:
  - reuse `progress.json` and raw outputs when the script supports resume
  - fail if resume state no longer matches the current sampled task set

## Monitoring Expectations

Require long runs to expose enough signal for unattended monitoring:

- progress lines in logs
- stage-local summaries
- explicit incident records on failure
- resumable progress files where feasible

If those signals are missing, add them before trusting the next long unattended run.
