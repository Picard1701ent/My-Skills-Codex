---
name: task-memory-ledger
description: Maintain durable task memory for complex, multi-step, or multi-folder work. Use when Codex needs to track long-running progress across sessions for reproductions, baselines, experiments, implementations, audits, or any complex task with multiple units that each need their own memory.md plus a root-level memory.md and memory_index.md.
---

# Task Memory Ledger

Use this skill when work is too large to fit reliably in conversation memory and needs a visible, durable record on disk. The pattern is:

- root `memory.md`: overall objective, global status, blockers, and next actions
- per-unit `memory.md`: status and execution history for each baseline, subtask, repo, or component
- root `memory_index.md`: generated map of unit memory files and short summaries

## Establish the Ledger

1. Identify the target root.
   - Prefer an explicit path from the user.
   - Otherwise use the current working directory.
2. Identify the task units.
   - For baseline reproduction, default to `baselines/*`.
   - For implementation work, use the smallest stable folders that own independent progress, such as packages, services, experiments, or milestones.
3. Create missing memory files with:

```bash
python3 /home/ubuntu/.codex/skills/task-memory-ledger/scripts/memory_ledger.py init --root <root> --unit-glob '<glob>'
```

Use `--unit-glob` multiple times when the task spans several folder groups.

## Update During Work

Read the relevant root and unit memory before acting. Update memory after meaningful events, not only at the end:

- command launched or completed
- experiment result observed
- blocker discovered or resolved
- design decision made
- artifact, checkpoint, log, report, or PR created
- next action changes

Append a concise execution record with:

```bash
python3 /home/ubuntu/.codex/skills/task-memory-ledger/scripts/memory_ledger.py append \
  --memory <path/to/memory.md> \
  --title "short event title" \
  --status "done|running|blocked|planned" \
  --command "command or action, if relevant" \
  --result "what happened" \
  --next "next concrete action"
```

Then rebuild the root index:

```bash
python3 /home/ubuntu/.codex/skills/task-memory-ledger/scripts/memory_ledger.py sync --root <root> --unit-glob '<glob>'
```

## Memory Content Rules

- Keep memory factual and operational. Prefer exact paths, run IDs, commands, metrics, and artifact locations.
- Separate current status from historical logs.
- Preserve useful history; append records instead of deleting past execution evidence.
- Keep entries concise enough that a future agent can scan them quickly.
- Write in the user's language unless the repo already has a clear documentation language.
- Do not record secrets, API keys, private tokens, or raw sensitive data.
- If a claim depends on a file or artifact, include the path.

## Default File Shapes

Root `memory.md`:

```md
# Memory

Last updated: <UTC timestamp>

## Current Objective
## Overall Status
## Active Units
## Global Blockers
## Next Actions
## Recent Updates
```

Unit `memory.md`:

```md
# Memory

Last updated: <UTC timestamp>

## Unit Summary
## Current Status
## Execution Log
## Artifacts / Evidence
## Open Problems
## Next Actions
```

Generated root `memory_index.md`:

```md
# Memory Index

Generated: <UTC timestamp>

| Unit | Memory | Status | Summary | Latest update |
| --- | --- | --- | --- | --- |
```

## Relationship to Other Planning Skills

- Use `plan-md-ledger` for one approved implementation plan and progress checkoff.
- Use this skill for durable multi-unit state, execution logs, and cross-session handoff.
- When both apply, keep `plan.md` as the tactical plan and `memory.md` files as the operational memory.
