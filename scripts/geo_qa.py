#!/usr/bin/env python3
"""GEO content QA on markdown files. Close local feedback loop.

Usage:
  python scripts/geo_qa.py content/_drafts/foo.md
  python scripts/geo_qa.py content/en/first-post.md content/es/first-post.md
  python scripts/geo_qa.py content/_drafts --strict
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from blog_chat.features.posts.parser import parse_markdown_file

_MD_IMG_RE = re.compile(r"!\[([^\]]*)\]\([^)]+\)")
_MD_LINK_RE = re.compile(r"\[[^\]]+\]\((https?://[^)]+)\)")
_HTML_IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
_HTML_LINK_RE = re.compile(r'href="(https?://[^"]+)"')
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_HASHTAG_HEADING_RE = re.compile(r"^#{1,6}\s+.+\?\s*$", re.M)
_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9]+")
_STAT_RE = re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:%|percent|por ciento|k|m|b|ms|s|x)\b", re.I)


def _iter_markdown_paths(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            for entry in sorted(path.rglob("*.md")):
                if "_trash" in entry.parts:
                    continue
                files.append(entry)
        elif path.is_file() and path.suffix == ".md":
            files.append(path)
    return files


def _sentence_lengths(text: str) -> list[int]:
    plain = re.sub(r"`[^`]*`", " ", text)
    plain = re.sub(r"```.*?```", " ", plain, flags=re.S)
    plain = re.sub(r"[*_#>|]", " ", plain)
    lengths = []
    for sentence in _SENT_SPLIT_RE.split(plain):
        words = _WORD_RE.findall(sentence)
        if words:
            lengths.append(len(words))
    return lengths


def analyze_post(post: dict, raw: str) -> list[tuple[str, str, str]]:
    """Return list of (level, code, message). Levels: error|warn|info."""
    findings: list[tuple[str, str, str]] = []
    title = (post.get("title") or "").strip()
    description = (post.get("description") or "").strip()
    body = post.get("content") or ""
    lang = post.get("lang") or "mixed"

    if not title:
        findings.append(("error", "missing_title", "Frontmatter title is empty"))
    if not description:
        findings.append(
            (
                "error",
                "missing_description",
                "Frontmatter description is empty (needed for meta/llms.txt/schema)",
            )
        )
    elif len(description) < 40:
        findings.append(
            ("warn", "short_description", f"Description is short ({len(description)} chars)")
        )

    if not body.strip():
        findings.append(("error", "empty_body", "Post body is empty"))
        return findings

    sentences = _sentence_lengths(body)
    long_sentences = [n for n in sentences if n > 28]
    if long_sentences:
        findings.append(
            (
                "warn",
                "long_sentences",
                f"{len(long_sentences)} sentence(s) over 28 words (max {max(long_sentences)})",
            )
        )

    images = _MD_IMG_RE.findall(body) + [
        m.group(0) for m in _HTML_IMG_RE.finditer(body)
    ]
    missing_alt = []
    for img in _MD_IMG_RE.finditer(body):
        if not img.group(1).strip():
            missing_alt.append(img.group(0)[:60])
    for img in _HTML_IMG_RE.finditer(body):
        tag = img.group(0)
        if not re.search(r'alt="[^"]+"', tag):
            missing_alt.append(tag[:60])
    if missing_alt:
        findings.append(
            ("error", "missing_alt", f"{len(missing_alt)} image(s) without descriptive alt")
        )

    external_links = set(_MD_LINK_RE.findall(body)) | set(_HTML_LINK_RE.findall(body))
    if not external_links:
        findings.append(
            (
                "warn",
                "no_external_links",
                "No external links (weak citability signal for GEO)",
            )
        )

    if not _STAT_RE.search(body):
        findings.append(
            (
                "warn",
                "no_statistics",
                "No concrete statistics/numbers found (KDD GEO: statistics improve visibility)",
            )
        )

    question_headings = _HASHTAG_HEADING_RE.findall(body)
    if lang in {"en", "es"} and len(question_headings) == 0 and len(sentences) >= 8:
        findings.append(
            (
                "info",
                "no_question_headings",
                "No question-format headings (useful for guides/FAQs, optional for diary posts)",
            )
        )

    if description and body.strip():
        first_para = re.split(r"\n\s*\n", body.strip(), maxsplit=1)[0]
        first_words = _WORD_RE.findall(first_para)[:40]
        desc_words = set(_WORD_RE.findall(description.lower()))
        overlap = sum(1 for w in first_words if w.lower() in desc_words)
        if first_words and overlap == 0:
            findings.append(
                (
                    "info",
                    "description_body_gap",
                    "Description words do not appear in the opening paragraph",
                )
            )

    return findings


def format_report(path: Path, findings: list[tuple[str, str, str]]) -> str:
    if not findings:
        return f"OK  {path}"
    lines = [f"QA  {path}"]
    order = {"error": 0, "warn": 1, "info": 2}
    for level, code, message in sorted(findings, key=lambda f: order.get(f[0], 9)):
        lines.append(f"  [{level:5}] {code}: {message}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GEO content QA on markdown posts")
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown files or directories")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any error-level finding exists (default: always 0)",
    )
    args = parser.parse_args(argv)

    files = _iter_markdown_paths(args.paths)
    if not files:
        print("No markdown files found", file=sys.stderr)
        return 2

    exit_code = 0
    for path in files:
        raw = path.read_text(encoding="utf-8")
        post = parse_markdown_file(path)
        if not post:
            print(f"SKIP {path} (unparseable)")
            continue
        findings = analyze_post(post, raw)
        print(format_report(path, findings))
        if args.strict and any(level == "error" for level, _, _ in findings):
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
