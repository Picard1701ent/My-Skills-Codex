#!/usr/bin/env python3
"""
Fetch an open-source repo for a paper.

Supports:
- git clone for GitHub/GitLab/Bitbucket URLs
- download + unzip for direct .zip URLs

This is a convenience helper for $paper-ideation DEEPDIVE. It is intentionally simple.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def run(cmd: list[str], cwd: Path | None = None) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(cmd)}")


def normalize_repo_url(url: str) -> str:
    u = url.strip()
    # Strip common decorations
    u = u.strip("()[]{}<>")
    # Convert GitHub web URLs with /tree/<ref> to repo root
    m = re.match(r"^(https?://github\.com/[^/]+/[^/]+)(/tree/.*)?$", u)
    if m:
        u = m.group(1)
    # Remove trailing slash
    u = u.rstrip("/")
    return u


def default_dest_from_url(url: str, dest_root: Path) -> Path:
    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) >= 2:
        name = f"{parts[0]}-{parts[1]}"
    else:
        name = re.sub(r"[^a-zA-Z0-9_.-]+", "_", parsed.netloc + parsed.path)[:80]
    return dest_root / name


def is_zip_url(url: str) -> bool:
    return url.lower().endswith(".zip")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Fetch a code repo (clone or download zip).")
    ap.add_argument("--url", required=True, help="Repo URL (GitHub/GitLab/etc) or direct zip URL.")
    ap.add_argument("--dest", default="", help="Destination folder. Defaults to --dest-root/<owner-repo>.")
    ap.add_argument("--dest-root", default="repos", help="Root folder for auto destination. Default: repos")
    ap.add_argument("--force", action="store_true", help="Delete destination if it exists.")
    args = ap.parse_args(argv)

    url = normalize_repo_url(args.url)
    dest_root = Path(args.dest_root).expanduser().resolve()
    dest = Path(args.dest).expanduser().resolve() if args.dest else default_dest_from_url(url, dest_root)

    if dest.exists():
        if not args.force:
            print(f"[error] Destination exists: {dest} (use --force to overwrite)", file=sys.stderr)
            return 2
        shutil.rmtree(dest)

    dest.parent.mkdir(parents=True, exist_ok=True)

    if is_zip_url(url):
        if shutil.which("wget") is None:
            print("[error] wget not found (required for zip download)", file=sys.stderr)
            return 2
        if shutil.which("unzip") is None:
            print("[error] unzip not found (required for zip download)", file=sys.stderr)
            return 2
        tmp_zip = dest.with_suffix(".zip")
        print(f"[info] Downloading zip -> {tmp_zip}")
        run(["wget", "-O", str(tmp_zip), url])
        dest.mkdir(parents=True, exist_ok=True)
        print(f"[info] Unzipping -> {dest}")
        run(["unzip", "-q", str(tmp_zip), "-d", str(dest)])
        try:
            tmp_zip.unlink(missing_ok=True)  # py>=3.8
        except TypeError:
            if tmp_zip.exists():
                tmp_zip.unlink()
        print(f"[ok] Fetched zip into: {dest}")
        return 0

    if shutil.which("git") is None:
        print("[error] git not found (required for clone)", file=sys.stderr)
        return 2

    clone_url = url
    # Add .git for common hosts if missing (safe for git, but not required)
    if any(h in clone_url.lower() for h in ("github.com/", "gitlab.com/", "bitbucket.org/")) and not clone_url.endswith(".git"):
        clone_url = clone_url + ".git"

    print(f"[info] Cloning -> {dest}")
    run(["git", "clone", "--depth", "1", clone_url, str(dest)])
    print(f"[ok] Cloned into: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

