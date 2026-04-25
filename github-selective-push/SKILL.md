---
name: github-selective-push
description: Commit and push only specific user-selected files from a local Git repository to a GitHub remote, without accidentally staging unrelated work. Use when Codex needs to set up Git identity or SSH access, verify the remote, stage a narrow file list, handle ignored paths with force-add when explicitly requested, resolve first-push divergence with fetch or rebase, and push the result to GitHub.
---

# GitHub Selective Push

## Overview

Use this skill to perform a narrow, auditable GitHub upload from an existing local repository. Favor safety over convenience: inspect state first, stage only the files the user named, and confirm what is actually in the index before committing.

## Workflow

1. Inspect repository state.

- Run `git rev-parse --is-inside-work-tree`, `git remote -v`, and `git status --short --ignored`.
- If the directory is not a Git repository, run `git init`.
- If `origin` is missing, add the user-provided GitHub SSH or HTTPS remote.

2. Configure local Git identity when needed.

- Set repository-local identity instead of global unless the user asks otherwise.
- Use:
  ```bash
  git config user.name "<github-name>"
  git config user.email "<github-email>"
  ```

3. Prepare GitHub SSH access when the remote uses SSH.

- Check for `~/.ssh/id_ed25519` and `~/.ssh/id_ed25519.pub`.
- If missing, generate them with:
  ```bash
  ssh-keygen -t ed25519 -C "<github-email>" -f ~/.ssh/id_ed25519 -N ""
  ```
- Show the public key with `cat ~/.ssh/id_ed25519.pub` so the user can add it to GitHub.
- If `ssh -T git@github.com` fails with host-key verification, append the host key with:
  ```bash
  ssh-keyscan github.com >> ~/.ssh/known_hosts
  ```
- Confirm connectivity with:
  ```bash
  ssh -T git@github.com
  ```

4. Stage only the requested files.

- Never run `git add .` unless the user explicitly wants a broad commit.
- Add exact paths only.
- If the requested file lives under an ignored path such as `result/`, use `git add -f <path>` only when the user explicitly asked to upload that file.
- Verify the staged set with:
  ```bash
  git diff --cached --name-status
  ```

5. Commit only after the staged set is correct.

- Use a concise Conventional Commit message when practical, such as:
  ```bash
  git commit -m "chore: add experiment reward plot"
  ```

6. Push and handle first-push divergence cleanly.

- Rename the branch to `main` if needed with `git branch -M main`.
- Push with:
  ```bash
  git push -u origin main
  ```
- If push is rejected because remote `main` already contains an initial commit, run:
  ```bash
  git fetch origin main
  git rebase origin/main
  git push -u origin main
  ```
- Avoid force-pushing unless the user explicitly requests it and understands the consequence.

## Operating Rules

- Keep unrelated untracked or modified files out of the commit.
- Respect existing `.gitignore` rules unless the user explicitly asks to override them for a specific path.
- Report the exact file paths staged, the commit hash, and whether push succeeded.
- If a push fails, explain the concrete blocker and the next corrective command.

## Common Patterns

For a single ignored artifact:

```bash
git add -f result/analysis/example.png
git diff --cached --name-status
git commit -m "chore: add experiment figure"
git push -u origin main
```

For a few specific source files:

```bash
git add README.md configs core scripts tests
git diff --cached --name-status
git commit -m "chore: initial import"
git push -u origin main
```
