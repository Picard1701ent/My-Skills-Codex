#!/usr/bin/env python3
"""Maintain root and per-unit memory.md ledgers for complex tasks."""

from __future__ import annotations

import argparse
import glob
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT_TEMPLATE = """# Memory

Last updated: {timestamp}

## Current Objective
- TODO: State the overall task objective.

## Overall Status
- planned

## Active Units
- TODO: List active units or run `sync` to rebuild `memory_index.md`.

## Global Blockers
- None recorded.

## Next Actions
- TODO: Record the next concrete action.

## Recent Updates
"""


UNIT_TEMPLATE = """# Memory

Last updated: {timestamp}

## Unit Summary
- TODO: Describe what this unit owns.

## Current Status
- planned

## Execution Log

## Artifacts / Evidence
- None recorded.

## Open Problems
- None recorded.

## Next Actions
- TODO: Record the next concrete action for this unit.
"""


INDEX_HEADER = """# Memory Index

Generated: {timestamp}

| Unit | Memory | Status | Summary | Latest update |
| --- | --- | --- | --- | --- |
"""


@dataclass(frozen=True)
class UnitSummary:
    unit: Path
    memory: Path
    status: str
    summary: str
    latest_update: str


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def resolve_root(root: str | Path) -> Path:
    return Path(root).expanduser().resolve()


def discover_units(root: Path, patterns: Iterable[str]) -> list[Path]:
    units: set[Path] = set()
    for pattern in patterns:
        for match in glob.glob(str(root / pattern)):
            path = Path(match).resolve()
            if path.is_dir() and path != root:
                units.add(path)
    return sorted(units)


def ensure_root_memory(root: Path) -> Path:
    memory = root / "memory.md"
    if not memory.exists():
        memory.write_text(ROOT_TEMPLATE.format(timestamp=utc_now()), encoding="utf-8")
    return memory


def ensure_unit_memory(unit: Path) -> Path:
    memory = unit / "memory.md"
    if not memory.exists():
        memory.write_text(UNIT_TEMPLATE.format(timestamp=utc_now()), encoding="utf-8")
    return memory


def replace_last_updated(text: str, timestamp: str) -> str:
    pattern = r"^Last updated: .*$"
    replacement = f"Last updated: {timestamp}"
    if re.search(pattern, text, flags=re.MULTILINE):
        return re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE)
    return text.rstrip() + f"\n\n{replacement}\n"


def replace_section_first_item(text: str, heading: str, value: str) -> str:
    pattern = rf"(^## {re.escape(heading)}\s*\n)(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    replacement = f"\\1- {value}\n"
    if match:
        return re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE | re.DOTALL)
    return text.rstrip() + f"\n\n## {heading}\n- {value}\n"


def append_memory_entry(
    memory: Path,
    title: str,
    status: str | None = None,
    command: str | None = None,
    result: str | None = None,
    next_action: str | None = None,
    note: str | None = None,
) -> None:
    timestamp = utc_now()
    memory.parent.mkdir(parents=True, exist_ok=True)
    if not memory.exists():
        memory.write_text(ROOT_TEMPLATE.format(timestamp=timestamp), encoding="utf-8")

    text = replace_last_updated(memory.read_text(encoding="utf-8"), timestamp)
    if status:
        text = replace_section_first_item(text, "Current Status", status)
    if next_action:
        text = replace_section_first_item(text, "Next Actions", next_action)
    text = text.rstrip()
    lines = [f"### {timestamp} - {title}"]
    if status:
        lines.append(f"- Status: {status}")
    if command:
        lines.append(f"- Command: `{command}`")
    if result:
        lines.append(f"- Result: {result}")
    if next_action:
        lines.append(f"- Next: {next_action}")
    if note:
        lines.append(f"- Note: {note}")

    entry = "\n".join(lines)
    memory.write_text(f"{text}\n\n{entry}\n", encoding="utf-8")


def extract_section_first_item(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\s*$"
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return ""
    tail = text[match.end() :].split("\n## ", 1)[0]
    for raw_line in tail.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        return line
    return ""


def extract_latest_update(text: str) -> str:
    last_updated = re.search(r"^Last updated:\s*(.+)$", text, flags=re.MULTILINE)
    if last_updated:
        return last_updated.group(1).strip()
    headings = re.findall(r"^###\s+(.+)$", text, flags=re.MULTILINE)
    return headings[-1].strip() if headings else ""


def one_line(value: str) -> str:
    return " ".join(value.strip().split())


def extract_memory_summary(unit: Path) -> UnitSummary:
    memory = unit / "memory.md"
    text = memory.read_text(encoding="utf-8") if memory.exists() else ""
    status = extract_section_first_item(text, "Current Status") or "unknown"
    summary = extract_section_first_item(text, "Unit Summary") or "No summary recorded."
    latest_update = extract_latest_update(text) or "unknown"
    return UnitSummary(
        unit=unit,
        memory=memory,
        status=one_line(status),
        summary=one_line(summary),
        latest_update=one_line(latest_update),
    )


def markdown_escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def write_memory_index(root: Path, units: list[Path]) -> Path:
    timestamp = utc_now()
    rows = []
    for unit in units:
        summary = extract_memory_summary(unit)
        rows.append(
            "| {unit} | {memory} | {status} | {summary} | {latest} |".format(
                unit=markdown_escape_cell(display_path(summary.unit, root)),
                memory=markdown_escape_cell(display_path(summary.memory, root)),
                status=markdown_escape_cell(summary.status),
                summary=markdown_escape_cell(summary.summary),
                latest=markdown_escape_cell(summary.latest_update),
            )
        )

    index = root / "memory_index.md"
    body = INDEX_HEADER.format(timestamp=timestamp)
    if rows:
        body += "\n".join(rows) + "\n"
    else:
        body += "| _No units found_ | _None_ | _unknown_ | _No unit glob matched directories._ | _n/a_ |\n"
    index.write_text(body, encoding="utf-8")
    return index


def command_init(args: argparse.Namespace) -> None:
    root = resolve_root(args.root)
    root.mkdir(parents=True, exist_ok=True)
    root_memory = ensure_root_memory(root)
    units = discover_units(root, args.unit_glob)
    for unit in units:
        ensure_unit_memory(unit)
    index = write_memory_index(root, units)
    print(f"root_memory={root_memory}")
    print(f"memory_index={index}")
    print(f"units={len(units)}")


def command_append(args: argparse.Namespace) -> None:
    memory = Path(args.memory).expanduser().resolve()
    append_memory_entry(
        memory=memory,
        title=args.title,
        status=args.status,
        command=args.command,
        result=args.result,
        next_action=args.next,
        note=args.note,
    )
    print(f"updated={memory}")


def command_sync(args: argparse.Namespace) -> None:
    root = resolve_root(args.root)
    ensure_root_memory(root)
    units = discover_units(root, args.unit_glob)
    for unit in units:
        ensure_unit_memory(unit)
    index = write_memory_index(root, units)
    print(f"memory_index={index}")
    print(f"units={len(units)}")


def command_status(args: argparse.Namespace) -> None:
    root = resolve_root(args.root)
    print(f"Root: {root}")
    root_memory = root / "memory.md"
    print(f"Root memory: {root_memory if root_memory.exists() else 'missing'}")
    index = root / "memory_index.md"
    print(f"Memory index: {index if index.exists() else 'missing'}")
    units = discover_units(root, args.unit_glob)
    print(f"Units: {len(units)}")
    for unit in units:
        summary = extract_memory_summary(unit)
        print(f"- {display_path(unit, root)} [{summary.status}]: {summary.summary}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create missing root and unit memory files.")
    init_parser.add_argument("--root", required=True, help="Task root directory.")
    init_parser.add_argument(
        "--unit-glob",
        action="append",
        default=[],
        help="Glob relative to root for unit directories. Repeatable.",
    )
    init_parser.set_defaults(func=command_init)

    append_parser = subparsers.add_parser("append", help="Append one progress record to a memory.md file.")
    append_parser.add_argument("--memory", required=True, help="memory.md path to update.")
    append_parser.add_argument("--title", required=True, help="Short event title.")
    append_parser.add_argument("--status", help="Status value, such as planned, running, done, or blocked.")
    append_parser.add_argument("--command", help="Command or action taken.")
    append_parser.add_argument("--result", help="Observed result.")
    append_parser.add_argument("--next", help="Next concrete action.")
    append_parser.add_argument("--note", help="Additional concise note.")
    append_parser.set_defaults(func=command_append)

    sync_parser = subparsers.add_parser("sync", help="Rebuild memory_index.md from unit memories.")
    sync_parser.add_argument("--root", required=True, help="Task root directory.")
    sync_parser.add_argument(
        "--unit-glob",
        action="append",
        default=[],
        help="Glob relative to root for unit directories. Repeatable.",
    )
    sync_parser.set_defaults(func=command_sync)

    status_parser = subparsers.add_parser("status", help="Print a concise ledger overview.")
    status_parser.add_argument("--root", required=True, help="Task root directory.")
    status_parser.add_argument(
        "--unit-glob",
        action="append",
        default=[],
        help="Glob relative to root for unit directories. Repeatable.",
    )
    status_parser.set_defaults(func=command_status)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "unit_glob") and not args.unit_glob:
        args.unit_glob = ["baselines/*"]
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
