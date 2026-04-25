---
name: repro-orchestrator
description: Plan and supervise end-to-end model/paper reproduction projects. Use when a user asks to reproduce a method, define an experiment roadmap, manage resources/risks, or produce a final reproducibility report.
---

# Repro Orchestrator

## Overview
Use this skill to turn a vague reproduction request into a concrete, auditable execution plan.
It focuses on planning, sequencing, and acceptance criteria before heavy compute is spent.

## When To Use
Use this skill when the user asks any of the following:
- "Reproduce this paper/model"
- "Plan benchmark runs for multiple models"
- "Design a roadmap with budget/timeline and checkpoints"
- "Prepare final reproducibility report and evidence"

Do not use this skill for one-off bug fixes or a single script tweak.

## Core Workflow
1. **Scope the target**
   - Capture objective, target metrics, target datasets, and constraints.
   - Define done criteria (for example: metric threshold, required artifacts).
2. **Audit prerequisites**
   - Environment, dependency versions, hardware limits, API quotas, dataset availability, legal/safety constraints.
3. **Create run architecture**
   - Build model x benchmark matrix.
   - Split into smoke run and full run.
   - Define retry policy and max budget.
4. **Define artifacts and telemetry**
   - Required logs, summaries, token/API usage, cost, elapsed time, incidents.
5. **Execution checkpoints**
   - Checkpoint A: smoke pass/fail
   - Checkpoint B: full-run launch gate
   - Checkpoint C: final validation gate
6. **Report and decision**
   - Summarize results vs done criteria.
   - List deviations and next actions.

## Mandatory Deliverables
Create/update these files for each reproduction project:
- `repro_plan.md` (scope, assumptions, roadmap)
- `experiment_manifest.yaml` (matrix + runtime params)
- `runbook.md` (commands + monitoring + recovery)
- `final_report.md` (results + incidents + verdict)

Use templates:
- `references/repro-plan-template.md`
- `references/experiment-manifest-template.yaml`

## Quality Gates
Before moving from smoke -> full, verify:
- At least one sample run succeeds on each benchmark type.
- Logging and summary paths are confirmed.
- Token/API/cost fields are present in summary outputs.
- Failure handling path is validated.

## Fast Start
- Initialize boilerplate docs with `scripts/init_repro_docs.py`.
- Fill scope and matrix first; avoid running full jobs until smoke passes.
