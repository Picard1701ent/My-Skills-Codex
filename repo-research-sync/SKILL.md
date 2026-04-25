---
name: repo-research-sync
description: Maintain a project-local research.md while reading a repository, folder, or codebase for analysis or planning. Use when Codex must inspect multiple files or infer project structure, behavior, or intent before proposing a plan, especially when the user wants to verify Codex's understanding and prevent planning drift.
---

# Repo Research Sync

Use this skill to keep a user-visible record of current understanding in `<target-root>/research.md` while exploring a codebase. Treat that file as the alignment artifact for what is confirmed, what is inferred, and what still needs user confirmation before a final plan.

## Establish the Target Root

- Identify the project or folder root before deep exploration.
- Prefer an explicit user-provided path. Otherwise infer the smallest root that contains the files being analyzed.
- Ask one concise question only if multiple plausible roots would change where `research.md` should live.
- Use `<target-root>/research.md` as the canonical research file for the task.

## Reconcile Existing Research

- Read an existing `research.md` before continuing with repo exploration.
- Preserve conclusions that are still supported by the current codebase.
- Replace stale claims instead of leaving contradictory text behind.
- Refresh a `Delta from previous review` section whenever prior content existed.

## Update During Exploration

- Update `research.md` while reading the repo, not only after exploration is complete.
- Record meaningful discoveries as soon as they affect current understanding, scope, or risk.
- Separate confirmed facts from inference.
- Cite repo-relative paths and line numbers when a claim depends on concrete code evidence.
- Keep the document concise and structured. Prefer revising sections in place over turning it into an append-only log.
- Match the user's language. Write in Chinese when the user is working in Chinese unless they ask otherwise.

## Keep `research.md` Focused

Use this default structure:

```md
# Research

## Task and user intent
## Current understanding
## Confirmed evidence from codebase
## Open questions
## Risks / likely drift points
## Pending user confirmations
## Delta from previous review
```

Apply these rules:

- Omit `Delta from previous review` when there was no prior file.
- Keep `Current understanding` to the model of the system, not a full implementation plan.
- Use `Confirmed evidence from codebase` for grounded facts only.
- Use `Open questions` and `Pending user confirmations` to expose uncertainty early.
- Use `Risks / likely drift points` for places where the current understanding may be wrong, incomplete, or likely to change after deeper inspection.

## Plan Gate

- Discuss tentative implementation directions when useful, but label them as provisional until `research.md` is confirmed.
- Pause before giving a final plan if the task required repo reading and understanding synthesis.
- After user corrections, update `research.md` first and only then continue with planning.
- Do not create extra alignment documents unless the user explicitly asks for them. `research.md` is the primary artifact for this workflow.
