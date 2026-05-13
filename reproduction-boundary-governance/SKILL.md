---
name: reproduction-boundary-governance
description: Enforce strict task, data, method, and evaluation boundary checks for paper or model reproduction before implementation or long runs. Use when reproducing papers, adapting methods to available data, classifying faithful versus adapted baselines, or requiring explicit user approval for any adaptive implementation.
---

# Reproduction Boundary Governance

## Core Rule

Before implementation or full runs, verify whether the reproduction target is still the same task, method, data contract, and evaluation protocol as the source work. Do not treat runnable code as sufficient evidence of faithful reproduction.

## Required Intake

Collect or infer these items before coding:

- Original task, prediction target, sample unit, and input/output format.
- Required data modalities, graph structure, auxiliary features, and preprocessing.
- Core method components and which ones are essential versus optional.
- Train/validation/test split, horizon, metrics, seeds, and reporting protocol.
- Available local data, code, compute limits, and missing prerequisites.

## Alignment Table

Create a compact table before implementation:

| Boundary | Source requirement | Local implementation | Status | Action |
| --- | --- | --- | --- | --- |
| Task | | | aligned / mismatch / unknown | |
| Target | | | aligned / mismatch / unknown | |
| Sample unit | | | aligned / mismatch / unknown | |
| Inputs | | | aligned / mismatch / unknown | |
| Core modules | | | aligned / mismatch / unknown | |
| Evaluation | | | aligned / mismatch / unknown | |

## Classification

Assign exactly one result category before comparing metrics:

- `faithful`: task, target, inputs, core modules, and evaluation are aligned.
- `adaptation`: task, target, data contract, or sample unit changes, but the method idea is intentionally preserved.
- `ablation`: a known component is removed or isolated to measure its effect.
- `diagnostic`: implementation exists only to inspect behavior or validate assumptions.
- `excluded`: required inputs, task setting, or core assumptions are unavailable or incompatible.

## Adaptation Approval Gate

Any adaptive implementation requires explicit user approval before coding, training, or launching long runs. This includes replacing targets, vertices, modalities, auxiliary data, distributed settings, official code, or unavailable inputs.

Use this proposal template:

```md
## Adaptation Proposal

Original method:
Original task:
Original prediction target:
Original sample unit / graph vertex:
Original required inputs:
Original core components:

Broken boundary:
Why faithful reproduction is not possible:

Proposed adaptation:
New task:
New prediction target:
New sample unit / graph vertex:
Inputs to be used:
Components preserved:
Components removed or replaced:
New method name:
Result category:
Expected risk:

User approval required before implementation: yes
```

## Naming Rules

- Use the original method name only for `faithful` reproduction.
- Use `Method-Adapted` when the task or data contract changes.
- Use `Method-TargetName` when the prediction target or sample unit changes.
- Use `Method-w/o-X` when a component is intentionally removed.
- Use `Method-Inspired` when only the high-level idea remains.
- Avoid exposing internal labels such as `core`, `lite`, `proxy`, or `fallback` in final tables.

## Long-Run Gate

Do not start full or expensive runs until all are true:

- Alignment table and classification are recorded.
- Method name and result category are fixed.
- No unapproved adaptation or fallback remains.
- Smoke run covers data loading, forward pass, backward pass, validation, and metric logging.
- Split, horizon, normalization, seed, metric definitions, run command, and code version are captured.

## Manifest Requirements

Record for every reproduced method:

- method name, category, source reference, and implementation source.
- task, target, sample unit, inputs, outputs, and graph/data assumptions.
- implemented components, omitted components, replacements, and deviations.
- split, horizon, metrics, seed, command, code version, timestamp, and hardware.
- approval record for every adaptation.

## Result Reporting

Keep faithful reproductions, adapted baselines, ablations, diagnostics, and excluded methods in separate sections. Do not rank adapted or diagnostic results as if they were faithful baselines. For excluded methods, state the missing boundary and why self-implementation or substitution would no longer be faithful.

## Agent Workflow

1. Read the source paper or official implementation enough to identify boundaries.
2. Inspect local data and existing code before proposing implementation.
3. Build the alignment table and classification.
4. Ask the user only for true boundary decisions that cannot be inferred.
5. Implement only after boundaries and approvals are fixed.
6. Smoke test before long runs.
7. Update memory or project notes with deviations, approvals, and final category.
