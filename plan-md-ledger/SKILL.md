---
name: plan-md-ledger
description: Persist the latest approved plan into a repo-local markdown ledger, auto-save it to `plan.md` when execution begins, archive replaced plans under `old_plan/`, and keep progress updated with strikethrough instead of deletion.
---

# Plan Md Ledger

## Overview

Use this skill when the latest approved plan should live on disk so Codex can keep executing against it without losing context. This skill maintains one active `plan.md`, archives replaced plans under `old_plan/`, and automatically updates progress while implementation is underway.

## Workflow

### 1. Establish the target root

- Use the user-provided repo or folder root when explicit.
- Otherwise use the current working directory.
- Keep all files directly under that root:
  - `plan.md`
  - `old_plan/`

### 2. Detect the latest approved plan

Use this step whenever a recent `<proposed_plan>` exists in the conversation.

- Treat the most recent `<proposed_plan>` as the candidate active plan.
- Do not create `plan.md` yet if the user is still discussing or revising the plan.
- Consider the plan approved when the user gives an execution signal such as:
  - "Implement the plan"
  - "按这个做"
  - "开始实现"
  - other clear instructions to execute the latest plan

### 3. Save the approved plan automatically

Use this step when the latest `<proposed_plan>` becomes approved, even if the user did not explicitly mention `plan.md`.

- If `<target-root>/plan.md` already exists, move it to `<target-root>/old_plan/`.
- Do not delete old plans.
- Archive filename format:
  - `old_plan/YYYYMMDD_HHMMSS_plan.md`
- Create a fresh `<target-root>/plan.md`.
- Copy the latest approved plan content into that file in Markdown.
- Preserve the plan wording; do not compress or rewrite it unless the user asks for a rewrite.

Recommended file shape:

```md
# Active Plan

Created: 2026-03-16 12:34:56 UTC

## Source
- Conversation-derived plan saved by Codex

## Plan
- Item 1
- Item 2
```

### 4. Update progress without deleting history

Use this step automatically while executing work that belongs to the active plan.

- Update the existing `<target-root>/plan.md`; do not create another active plan file.
- Mark completed items with Markdown strikethrough syntax `~~...~~`.
- Keep completed text visible. Do not delete completed items.
- If useful, append a short progress note such as `Done: implemented in current turn`.
- Leave pending items unchanged.
- For partial progress, keep the item unstruck and add a short inline note instead.

Example:

```md
- ~~Add memory bank runtime~~
- Wire retrieval into prompt builder (in progress)
- Add manifest metrics
```

### 5. Replace the active plan

Use this step when a new plan supersedes the current one.

- Treat the current `<target-root>/plan.md` as history.
- Move it into `old_plan/` using the archive filename format.
- Write the replacement plan into a new fresh `<target-root>/plan.md`.
- Never overwrite archived files in place.

## Rules

- Keep exactly one active plan file: `<target-root>/plan.md`.
- Keep all previous plans in `<target-root>/old_plan/`.
- Use UTC timestamps in archive filenames and optional metadata lines.
- Never delete old plans unless the user explicitly requests cleanup.
- Never remove completed tasks from `plan.md`; use strikethrough instead.
- If there is no approved plan yet, do not create `plan.md` preemptively.
- Do not auto-save a plan merely because `<proposed_plan>` was emitted; wait for an approval or execution signal.
- Once an approved plan has been saved, treat progress updates as the default during execution rather than requiring another user reminder.
- If the current task is unrelated to the active plan, do not force unrelated progress into `plan.md`.

## Trigger Examples

- "把这个计划写到 md 里，后面执行时持续更新"
- "保存当前 propose plan，旧计划归档，不要删"
- "做一个 active plan 文件，完成的任务划线"
- "新计划出来后把旧的 plan.md 移到 old_plan"
- "Implement the plan."
- "按刚才那个 plan 开始做"
- "照这个方案执行"
