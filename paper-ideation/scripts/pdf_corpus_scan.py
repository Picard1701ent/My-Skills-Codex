#!/usr/bin/env python3
"""
Scan a folder of PDFs and extract:
- best-effort title guess (metadata + first page)
- abstract snippet
- introduction snippet
- heuristic "gap sentences" from the intro

This script is intentionally deterministic; it does NOT summarize with an LLM.
Its output is meant to feed the $paper-ideation reasoning workflows.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional


@dataclass
class PaperExtract:
    path: str
    title_guess: str
    abstract: str
    introduction: str
    gap_sentences: list[str]
    code_links: list[str]
    extraction_method: str
    errors: list[str]


GAP_MARKERS = [
    # English
    r"\bhowever\b",
    r"\bbut\b",
    r"\bdespite\b",
    r"\bnevertheless\b",
    r"\bnonetheless\b",
    r"\byet\b",
    r"\bstill\b",
    r"\bremain(s|ed)?\b",
    r"\black(s|ed|ing)?\b",
    r"\blimited\b",
    r"\blimitation(s)?\b",
    r"\bchallenge(s)?\b",
    r"\bopen problem(s)?\b",
    r"\bgap(s)?\b",
    # Chinese (best-effort)
    r"然而",
    r"但是",
    r"尽管",
    r"不过",
    r"仍然",
    r"尚未",
    r"缺乏",
    r"不足",
    r"局限",
    r"挑战",
    r"问题",
]


def _read_pdf_text_pdfplumber(pdf_path: Path, max_pages: int) -> str:
    import pdfplumber  # type: ignore

    texts: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages[: max_pages or len(pdf.pages)]):
            try:
                t = page.extract_text() or ""
            except Exception:
                t = ""
            if t.strip():
                texts.append(t)
    return "\n\n".join(texts)


def _read_pdf_text_pypdf(pdf_path: Path, max_pages: int) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        # Common older name
        from PyPDF2 import PdfReader  # type: ignore

    reader = PdfReader(str(pdf_path))
    texts: list[str] = []
    pages = reader.pages
    n = min(len(pages), max_pages) if max_pages else len(pages)
    for i in range(n):
        try:
            t = pages[i].extract_text() or ""
        except Exception:
            t = ""
        if t.strip():
            texts.append(t)
    return "\n\n".join(texts)


def _read_pdf_text_pdftotext(pdf_path: Path, max_pages: int) -> str:
    # pdftotext doesn't support "max pages" uniformly across distros.
    # We accept this limitation and rely on the tool's speed.
    cmd = ["pdftotext", "-layout", str(pdf_path), "-"]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "pdftotext failed")
    return proc.stdout


def read_pdf_text(pdf_path: Path, max_pages: int) -> tuple[str, str, list[str]]:
    errors: list[str] = []
    # Try in an order that tends to work best.
    for method in ("pdfplumber", "pypdf", "pdftotext"):
        try:
            if method == "pdfplumber":
                text = _read_pdf_text_pdfplumber(pdf_path, max_pages)
            elif method == "pypdf":
                text = _read_pdf_text_pypdf(pdf_path, max_pages)
            else:
                text = _read_pdf_text_pdftotext(pdf_path, max_pages)
            if text.strip():
                return text, method, errors
            errors.append(f"{method}: extracted empty text")
        except Exception as e:
            errors.append(f"{method}: {type(e).__name__}: {e}")
            continue
    return "", "none", errors


def normalize_ws(s: str) -> str:
    s = s.replace("\u00ad", "")  # soft hyphen
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def _find_section(text: str, header_patterns: list[str], stop_patterns: list[str], max_chars: int) -> str:
    lower = text.lower()
    starts: list[int] = []
    for pat in header_patterns:
        m = re.search(pat, lower, flags=re.MULTILINE)
        if m:
            starts.append(m.end())
    if not starts:
        return ""
    start = min(starts)
    tail = text[start:]

    stop_idx = None
    lower_tail = tail.lower()
    for pat in stop_patterns:
        m = re.search(pat, lower_tail, flags=re.MULTILINE)
        if m:
            stop_idx = m.start()
            break
    chunk = tail[:stop_idx] if stop_idx is not None else tail
    chunk = normalize_ws(chunk)
    if max_chars and len(chunk) > max_chars:
        chunk = chunk[:max_chars].rstrip() + " ..."
    return chunk


def extract_abstract_and_intro(text: str, max_section_chars: int) -> tuple[str, str]:
    # Best-effort; different templates vary a lot.
    abstract = _find_section(
        text,
        header_patterns=[
            r"^\s*abstract\s*$",
            r"^\s*abstract\s*[:\-]\s*$",
            r"^\s*abstract\s",
        ],
        stop_patterns=[
            r"^\s*keywords\s*[:\-]?\s*$",
            r"^\s*index terms\s*[:\-]?\s*$",
            r"^\s*1\s*[\.\)]\s*introduction\s*$",
            r"^\s*introduction\s*$",
        ],
        max_chars=max_section_chars,
    )
    intro = _find_section(
        text,
        header_patterns=[
            r"^\s*1\s*[\.\)]\s*introduction\s*$",
            r"^\s*introduction\s*$",
            r"^\s*1\s*introduction\s*$",
        ],
        stop_patterns=[
            r"^\s*2\s*[\.\)]\s",
            r"^\s*related work\s*$",
            r"^\s*background\s*$",
            r"^\s*preliminaries\s*$",
        ],
        max_chars=max_section_chars,
    )

    # Fallback: if section headers aren't detected, take early pages as proxy.
    if not abstract:
        abstract = normalize_ws(text[: max_section_chars or 2000])
        if abstract:
            abstract = "[FALLBACK: early-pages snippet]\n" + abstract
    if not intro:
        # If no explicit intro header, take next chunk after abstract.
        start = len(abstract)
        intro_raw = text[start : start + (max_section_chars or 3000)]
        intro = normalize_ws(intro_raw)
        if intro:
            intro = "[FALLBACK: post-abstract snippet]\n" + intro
    return abstract, intro


def guess_title(text: str, pdf_path: Path) -> str:
    # Best-effort: first non-empty line with enough letters, but not "arXiv" etc.
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for l in lines[:30]:
        if len(l) < 12:
            continue
        if re.search(r"\barxiv\b", l.lower()):
            continue
        # Avoid common boilerplate
        if re.fullmatch(r"(abstract|introduction|keywords?)", l.lower()):
            continue
        # Title lines usually have letters and not too many punctuation.
        if re.search(r"[A-Za-z\u4e00-\u9fff]", l) and l.count(".") <= 2:
            return l[:160]
    return pdf_path.stem[:160]


def extract_gap_sentences(intro_text: str, max_sentences: int) -> list[str]:
    if not intro_text.strip():
        return []
    # Very simple sentence split; good enough for highlights.
    parts = re.split(r"(?<=[\.\!\?])\s+|(?<=[。！？])\s*", intro_text)
    marker_re = re.compile("|".join(GAP_MARKERS), flags=re.IGNORECASE)
    candidates: list[str] = []
    for s in parts:
        s = normalize_ws(s)
        if len(s) < 30:
            continue
        if marker_re.search(s):
            candidates.append(s)
    # Deduplicate while preserving order
    seen = set()
    out: list[str] = []
    for s in candidates:
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
        if len(out) >= max_sentences:
            break
    return out


def extract_code_links(text: str, max_links: int) -> list[str]:
    if not text.strip():
        return []
    # Extract obvious URLs; keep only likely code/project links.
    urls = re.findall(r"https?://[^\s\)\]\}<>\"']+", text)
    allow_hosts = (
        "github.com",
        "gitlab.com",
        "bitbucket.org",
        "huggingface.co",
        "gitee.com",
    )
    out: list[str] = []
    seen = set()
    for u in urls:
        u = u.rstrip(".,;:")
        ul = u.lower()
        if not any(h in ul for h in allow_hosts):
            continue
        if ul in seen:
            continue
        seen.add(ul)
        out.append(u)
        if len(out) >= max_links:
            break
    return out


def iter_pdfs(folder: Path) -> Iterable[Path]:
    for p in sorted(folder.rglob("*.pdf")):
        if p.is_file():
            yield p


def write_report_md(extracts: list[PaperExtract], out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# PDF Corpus Report")
    lines.append("")
    lines.append("## Index")
    lines.append("")
    lines.append("| # | File | Title guess | Abstract | Intro | Extractor |")
    lines.append("|---:|---|---|---:|---:|---|")
    for i, ex in enumerate(extracts, 1):
        has_abs = "yes" if ex.abstract.strip() else "no"
        has_intro = "yes" if ex.introduction.strip() else "no"
        lines.append(
            f"| {i} | `{Path(ex.path).name}` | {ex.title_guess.replace('|','/')} | {has_abs} | {has_intro} | {ex.extraction_method} |"
        )
    lines.append("")

    for i, ex in enumerate(extracts, 1):
        lines.append(f"## {i}. {ex.title_guess}")
        lines.append("")
        lines.append(f"- File: `{ex.path}`")
        lines.append(f"- Extraction: `{ex.extraction_method}`")
        if ex.errors:
            lines.append("- Notes:")
            for e in ex.errors[:6]:
                lines.append(f"  - {e}")
        lines.append("")
        lines.append("### Abstract (snippet)")
        lines.append("")
        lines.append("```")
        lines.append((ex.abstract or "").strip())
        lines.append("```")
        lines.append("")
        lines.append("### Introduction (snippet)")
        lines.append("")
        lines.append("```")
        lines.append((ex.introduction or "").strip())
        lines.append("```")
        lines.append("")
        lines.append("### Gap highlights (heuristic)")
        lines.append("")
        if ex.gap_sentences:
            for s in ex.gap_sentences:
                lines.append(f"- {s}")
        else:
            lines.append("- (none detected)")
        lines.append("")

        lines.append("### Code links (heuristic)")
        lines.append("")
        if ex.code_links:
            for u in ex.code_links:
                lines.append(f"- {u}")
        else:
            lines.append("- (none detected)")
        lines.append("")

    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Scan a folder of PDFs and extract abstract/introduction + gap highlights.")
    ap.add_argument("--folder", required=True, help="Folder containing PDFs (recursively scanned).")
    ap.add_argument("--max-pages", type=int, default=8, help="Max pages to extract per PDF (best-effort). Default: 8")
    ap.add_argument("--max-section-chars", type=int, default=3000, help="Max chars for abstract/intro snippets. Default: 3000")
    ap.add_argument("--gap-sentences", type=int, default=8, help="Max gap sentences to keep per paper. Default: 8")
    ap.add_argument("--max-links", type=int, default=8, help="Max code/project links to keep per paper. Default: 8")
    ap.add_argument("--out", default="paper_corpus_report.md", help="Markdown report output path.")
    ap.add_argument("--jsonl", default="", help="Optional JSONL output path for structured extracts.")
    args = ap.parse_args(argv)

    folder = Path(args.folder).expanduser().resolve()
    if not folder.exists() or not folder.is_dir():
        print(f"[error] --folder is not a directory: {folder}", file=sys.stderr)
        return 2

    pdfs = list(iter_pdfs(folder))
    if not pdfs:
        print(f"[error] No PDFs found under: {folder}", file=sys.stderr)
        return 2

    extracts: list[PaperExtract] = []
    for pdf_path in pdfs:
        text, method, errs = read_pdf_text(pdf_path, args.max_pages)
        text = normalize_ws(text)
        title = guess_title(text, pdf_path) if text else pdf_path.stem
        abstract, intro = extract_abstract_and_intro(text, args.max_section_chars) if text else ("", "")
        gaps = extract_gap_sentences(intro, args.gap_sentences)
        links = extract_code_links(text, args.max_links)
        extracts.append(
            PaperExtract(
                path=str(pdf_path),
                title_guess=title,
                abstract=abstract,
                introduction=intro,
                gap_sentences=gaps,
                code_links=links,
                extraction_method=method,
                errors=errs,
            )
        )

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_report_md(extracts, out_path)
    print(f"[ok] Wrote report: {out_path}")

    if args.jsonl:
        jsonl_path = Path(args.jsonl).expanduser().resolve()
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        with jsonl_path.open("w", encoding="utf-8") as f:
            for ex in extracts:
                f.write(json.dumps(asdict(ex), ensure_ascii=False) + "\n")
        print(f"[ok] Wrote jsonl: {jsonl_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
