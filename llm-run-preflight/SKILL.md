---
name: llm-run-preflight
description: Validate expensive or long-running LLM pipelines before launching the full run. Use when a workflow has multiple stages such as data generation, training, evaluation, or checkpoint selection and failures would waste significant time, compute, or API cost.
---

# LLM Run Preflight

## Overview

Use this skill to prove an LLM pipeline works end to end before committing to a long run.
Prefer a tiny, fixed-sample execution that exercises every critical stage and produces the same artifact types as the full experiment.

## Workflow

1. Define the full pipeline and the exact stages that must be exercised.
2. Shrink the workload aggressively without changing the code path:
   - Use the same scripts, models, prompts, and artifact layout.
   - Reduce sample counts, epochs, steps, or benchmark size only.
3. Run a minimal end-to-end smoke that covers:
   - data generation or task sampling
   - training or checkpoint creation
   - checkpoint loading
   - evaluation or legality checks
4. Verify each stage writes its expected artifacts:
   - logs
   - stage summaries
   - master summary
   - checkpoint or dataset outputs
5. Gate the long run on explicit pass criteria:
   - no empty dataset after filtering
   - checkpoint is loadable by downstream scripts
   - small-sample metrics are at least acceptable
   - no blocking environment failures
6. If comparing candidate checkpoints, run both on the same fixed small sample and write the selection decision to an artifact.

## Preflight Rules

- Keep the sample fixed and reusable so reruns are comparable.
- Prefer structure or legality metrics first when the downstream method depends on valid constrained outputs.
- Fail early on infrastructure issues instead of letting later stages discover them.
- Treat integrations such as tracking, logging, or external APIs as part of preflight, not optional extras.
- When a stage fails, record the failure class and stop before starting more expensive stages.

## Common Failure Checks

- API or backend reachability: verify the endpoint responds before waiting on full retries.
- Environment consistency: ensure the stage uses the same Python or conda env as the full run.
- Empty outputs: treat zero-sample datasets or zero-kept filtered outputs as blocking.
- Training integrations: disable or configure services like `wandb` if they can block unattended runs.
- Checkpoint compatibility: verify LoRA or adapter checkpoints can be loaded by the evaluation script that will consume them.

## Output

Produce a compact decision record with:

- the smoke run ids
- the candidate checkpoints compared
- the metrics used for gating
- the selected starting checkpoint
- the reason the alternative was rejected
