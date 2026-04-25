#!/usr/bin/env python3
from pathlib import Path
import argparse


def write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        return
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize reproduction planning documents.")
    parser.add_argument("--out", default=".", help="Output project directory")
    args = parser.parse_args()

    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    write_if_missing(out / "repro_plan.md", "# Reproduction Plan\n")
    write_if_missing(out / "experiment_manifest.yaml", "project:\n  name: sample\n")
    write_if_missing(out / "runbook.md", "# Runbook\n")
    write_if_missing(out / "final_report.md", "# Final Report\n")

    print(f"Initialized docs in {out}")


if __name__ == "__main__":
    main()
