---
name: sandbox-aware-test-ops
description: Run tests, smoke checks, training jobs, and benchmark pipelines when sandbox, network, GPU, package, or environment issues may block normal execution. Use when a task involves pytest/unittest, experiment scripts, conda environments, API-backed evaluation, model downloads, CUDA, or other commands that may need escalated permissions or a different runtime than the default shell.
---

# Sandbox-Aware Test Ops

## Overview

Use this skill when the user asks to run tests or experiments and the command may fail because of sandbox restrictions, missing network access, missing GPU visibility, or the wrong Python environment.
The goal is to keep execution moving: detect the blocker quickly, switch to the right conda env, and re-run with escalated permissions when needed.

## Workflow

1. Inspect the task before running it.
- Identify whether it is local-only, network-backed, GPU-backed, or environment-sensitive.
- Treat these as likely escalation cases: package install, model download, API calls, external datasets, CUDA checks, long training jobs, tmux/nohup, writes outside the workspace, or commands that already failed in sandbox for environment reasons.

2. Probe the environment instead of guessing.
- Check available conda envs with `conda env list`.
- If the command is Python-based, probe candidate envs with `conda run -n <env> python -c ...` for the exact imports the task needs, such as `torch`, `trl`, `transformers`, `pytest`, or task-specific packages.
- If GPU may matter, check `nvidia-smi` and prefer an env where the required stack is already installed.
- Prefer the project-specific env when the repo config already names one. Otherwise choose the first env that proves it has the required imports.

3. Start with the cheapest viable execution path.
- Use the sandbox only when the command is clearly local and the required packages are already present.
- If the task obviously needs network, GPU, or writes outside sandboxed roots, request escalated execution immediately instead of waiting for a predictable failure.
- If the first sandboxed attempt fails because of DNS, host resolution, authentication, blocked filesystem access, CUDA visibility, or missing packages in the default shell, re-run with escalated execution and the best conda env.

4. Escalate through the tool, not through chat.
- Use the execution tool's escalation flow directly with a short justification.
- Do not stop to ask the user in plain chat before making the escalation request.
- When possible, request a narrow reusable prefix rule that matches the command family, such as `pytest`, `conda run -n <env> python`, or `nvidia-smi`.

5. Preserve experiment hygiene.
- Keep the repo's normal artifact layout, logs, and summaries.
- For long or expensive runs, prefer smoke checks first unless the user explicitly wants the full run immediately.
- When a command fails, report whether the root cause was sandbox, API/network, missing package, wrong env, missing checkpoint/data, or code logic.

## Operating Rules

- Prefer `conda run -n <env>` over the system `python3` when the repo uses ML or evaluation stacks.
- Never assume the default shell has the right packages.
- If a command needs the internet, authenticated APIs, GPU, or non-workspace writes, bias toward escalated execution.
- If a command is important and fails in sandbox with a likely restrictions-related error, retry with escalation instead of giving up.
- If no suitable env exists, say exactly which imports are missing and which envs were checked.
- If credentials are missing, surface the exact variable or file expected.

## Common Patterns

For package/env mismatches:
```bash
conda env list
conda run -n multi-agent python -c "import torch, trl, transformers"
```

For network- or API-backed smoke tests:
```bash
conda run -n multi-agent python scripts/experiments/run_agent_smoke.py --worker-backend qwen --worker-model qwen14b-local --require-worker-api-calls
```
Run this with escalated permissions when the endpoint or auth may be blocked by sandbox.

For training or evaluation jobs:
```bash
conda run -n <best-env> python scripts/experiments/run_rl_train.py ...
conda run -n <best-env> python scripts/experiments/run_eval.py ...
```
Use escalated execution when GPU visibility, model downloads, or external APIs are required.
