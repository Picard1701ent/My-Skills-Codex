#!/usr/bin/env python3
"""
Generate a deterministic, LLM-free map of a code repository:
- key config/entrypoint files
- likely training/eval scripts
- likely core modules (model/data/loss/trainer)
- grep-based hits for common CLI/config frameworks

Designed to support $paper-ideation DEEPDIVE.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PATTERNS = {
    "entrypoint": [
        r"if __name__\s*==\s*['\"]__main__['\"]\s*:",
        r"^\s*def\s+main\s*\(",
    ],
    "argparse": [r"argparse\.ArgumentParser\s*\("],
    "hydra": [r"@hydra\.main\s*\(", r"hydra\.initialize", r"omegaconf"],
    "click": [r"@click\.command\s*\(", r"click\.group\s*\("],
    "typer": [r"\btyper\.Typer\s*\(", r"@app\.command\s*\("],
    "pytorch_lightning": [r"pytorch_lightning", r"\bTrainer\s*\("],
    "accelerate": [r"accelerate", r"Accelerator\s*\("],
    "deepspeed": [r"deepspeed"],
}


KEY_FILES = [
    "README.md",
    "README.rst",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "environment.yml",
    "environment.yaml",
    "Dockerfile",
    "Makefile",
]


def has_rg() -> bool:
    try:
        subprocess.run(["rg", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False


def rg_search(repo: Path, pattern: str) -> list[str]:
    # Return lines like: path:line:content
    cmd = [
        "rg",
        "-n",
        "--no-heading",
        "-S",
        "--hidden",
        "--glob",
        "!**/.git/**",
        "--glob",
        "!**/__pycache__/**",
        "--glob",
        "!**/.cache/**",
        "--glob",
        "!**/result/**",
        "--glob",
        "!**/outputs/**",
        "--glob",
        "!**/checkpoints/**",
        "--glob",
        "!**/summaries/**",
        "--glob",
        "!**/logs/**",
        "--glob",
        "!**/datasets/**",
        "--glob",
        "*.py",
        "--glob",
        "*.sh",
        "--glob",
        "*.md",
        "--glob",
        "*.yaml",
        "--glob",
        "*.yml",
        "--glob",
        "*.toml",
        "--glob",
        "*.json",
        pattern,
        str(repo),
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode not in (0, 1):  # 1 = no matches
        raise RuntimeError(proc.stderr.strip() or f"rg failed: {pattern}")
    out = []
    for line in proc.stdout.splitlines():
        if line.strip():
            out.append(line)
    return out


def py_search(repo: Path, pattern: re.Pattern[str]) -> list[str]:
    out: list[str] = []
    for p in iter_source_files(repo):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                out.append(f"{p}:{i}:{line.strip()}")
    return out


def iter_source_files(repo: Path) -> Iterable[Path]:
    for p in repo.rglob("*"):
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        if p.suffix.lower() not in (".py", ".sh", ".bash", ".yaml", ".yml", ".json", ".toml", ".md"):
            continue
        # Skip common junk
        parts = set(p.parts)
        if any(
            x in parts
            for x in (
                ".git",
                "__pycache__",
                ".cache",
                "venv",
                ".venv",
                "dist",
                "build",
                "result",
                "outputs",
                "checkpoints",
                "summaries",
                "logs",
                "datasets",
            )
        ):
            continue
        yield p


def find_key_files(repo: Path) -> list[Path]:
    found = []
    for name in KEY_FILES:
        p = repo / name
        if p.exists() and p.is_file():
            found.append(p)
    # Common config dirs
    for d in ("configs", "config", "conf"):
        p = repo / d
        if p.exists() and p.is_dir():
            found.append(p)
    return found


def guess_core_paths(repo: Path) -> list[Path]:
    # Heuristic: common folder names.
    candidates = []
    for d in ("src", "python", "scripts", "examples", "configs", "conf"):
        p = repo / d
        if p.exists():
            candidates.append(p)
    # If repo is a python package, include first-level packages.
    for p in repo.iterdir():
        if p.is_dir() and (p / "__init__.py").exists():
            candidates.append(p)
    return sorted({c.resolve() for c in candidates})


@dataclass
class HitGroup:
    name: str
    hits: list[str]


def collect_hits(repo: Path, max_hits_per_group: int) -> list[HitGroup]:
    groups: list[HitGroup] = []
    use_rg = has_rg()
    for name, patterns in PATTERNS.items():
        hits: list[str] = []
        for pat in patterns:
            if use_rg:
                found = rg_search(repo, pat)
            else:
                found = py_search(repo, re.compile(pat))
            hits.extend(found)
            if len(hits) >= max_hits_per_group:
                break
        # Dedup but keep order
        seen = set()
        uniq: list[str] = []
        for h in hits:
            if h in seen:
                continue
            seen.add(h)
            uniq.append(h)
            if len(uniq) >= max_hits_per_group:
                break
        groups.append(HitGroup(name=name, hits=uniq))
    return groups


def write_md(repo: Path, out_path: Path, groups: list[HitGroup]) -> None:
    lines: list[str] = []
    lines.append("# Codebase Map")
    lines.append("")
    lines.append(f"- Repo: `{repo}`")
    lines.append("")
    lines.append("## Key Files / Dirs")
    lines.append("")
    for p in find_key_files(repo):
        rel = p.relative_to(repo)
        kind = "dir" if p.is_dir() else "file"
        lines.append(f"- ({kind}) `{rel}`")
    lines.append("")
    lines.append("## Likely Core Paths")
    lines.append("")
    for p in guess_core_paths(repo):
        rel = p.relative_to(repo)
        lines.append(f"- `{rel}`")
    lines.append("")
    lines.append("## Grep Hits (heuristic)")
    lines.append("")
    for g in groups:
        lines.append(f"### {g.name}")
        lines.append("")
        if not g.hits:
            lines.append("- (no hits)")
            lines.append("")
            continue
        for h in g.hits:
            # Keep as-is; user/agent can open file at line.
            lines.append(f"- `{h}`")
        lines.append("")
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Generate a deterministic map of a repo for deep-dive explanation.")
    ap.add_argument("--repo", required=True, help="Path to the repository root.")
    ap.add_argument("--out", default="CODEBASE_MAP.md", help="Markdown output path.")
    ap.add_argument("--max-hits", type=int, default=20, help="Max grep hits per group. Default: 20")
    args = ap.parse_args(argv)

    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        print(f"[error] --repo is not a directory: {repo}", file=sys.stderr)
        return 2

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    groups = collect_hits(repo, args.max_hits)
    write_md(repo, out_path, groups)
    print(f"[ok] Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
