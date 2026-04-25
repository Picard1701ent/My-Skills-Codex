#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Collect benchmark summaries for one run_id.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--root", default="result/summaries")
    args = parser.parse_args()

    root = Path(args.root) / args.run_id
    if not root.exists():
        raise SystemExit(f"Missing run directory: {root}")

    files = sorted(root.glob("*/*.summary.json"))
    if not files:
        raise SystemExit("No benchmark summaries found.")

    print("model,benchmark,metric,prompt_tokens,completion_tokens,api_calls,elapsed_seconds")
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        metric = data.get("accuracy", data.get("score", ""))
        print(
            f"{data.get(model,)},{data.get(benchmark,)},{metric},"
            f"{data.get(prompt_tokens,)},{data.get(completion_tokens,)},"
            f"{data.get(api_calls,)},{data.get(elapsed_seconds,)}"
        )


if __name__ == "__main__":
    main()
