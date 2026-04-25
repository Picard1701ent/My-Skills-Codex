---
name: experiment-governance
description: Standardize experiment observability, artifact structure, metric schema, and incident handling. Use when runs must be auditable, comparable, and reproducible across models and benchmarks.
---

# Experiment Governance

## Overview
Use this skill to enforce consistent experiment records so results are traceable and reviewable.
It defines what must be logged, where artifacts live, and how failures are classified.

## When To Use
Use this skill when:
- Running multiple models/benchmarks
- Comparing runs across dates or environments
- Preparing results for reports, papers, or handoff

## Artifact Standard
For each `run_id`, require:
- Logs: `result/logs/<run_id>/<model>/<benchmark>.log`
- Summaries: `result/summaries/<run_id>/<model>/<benchmark>.summary.json`
- Master index: `result/summaries/<run_id>/master_summary.json`

## Required Summary Fields
Each benchmark summary should include:
- `benchmark`
- `model`
- main metric (`accuracy` or `score`)
- `prompt_tokens`
- `completion_tokens`
- `api_calls`
- `elapsed_seconds`
- `cost` (or explicit zero)

Reference schema in `references/metrics-schema.md`.

## Incident Management
Classify each failure with one code:
- `DATA_MISSING`
- `ENV_MISMATCH`
- `API_ERROR`
- `TIMEOUT`
- `LOGIC_BUG`
- `UNKNOWN`

For each incident, record:
- timestamp
- failed command
- stderr excerpt
- impact scope
- mitigation and retry decision

Use template: `references/incident-template.md`.

## Governance Checks
Before calling a run complete:
- All expected benchmark summaries exist.
- Summary fields pass schema checks.
- Failed jobs have incident entries.
- Master summary includes command + exit code + paths.

## Fast Start
- Run `scripts/collect_summaries.py --run-id <id>` to generate a compact table for review.
