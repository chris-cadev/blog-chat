#!/usr/bin/env python3
"""Pre-render mermaid diagrams to static SVG files.

Walks content/ for .md files, extracts ```mermaid blocks, renders each
to static/mermaid/<sha256>-dark.svg and <sha256>-light.svg.

Usage:
    python scripts/prerender_mermaid.py
    python scripts/prerender_mermaid.py --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

CONTENT_DIR = Path("content")
STATIC_DIR = Path("static")
MERMAID_DIR = STATIC_DIR / "mermaid"
MERMAID_FENCE_RE = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)
MERMAID_CAPTION_RE = re.compile(r"^%%\s*caption:\s*(.+)$", re.MULTILINE)
THEMES = [("dark", "dark"), ("light", "default")]


def _code_hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()[:16]


def _find_mermaid_blocks(content: str) -> list[str]:
    blocks = []
    for m in MERMAID_FENCE_RE.finditer(content):
        raw = m.group(1).strip()
        code = MERMAID_CAPTION_RE.sub("", raw).strip()
        if code:
            blocks.append(code)
    return blocks


def _find_content_files() -> list[Path]:
    files: list[Path] = []
    for p in CONTENT_DIR.rglob("*.md"):
        if "_trash" in p.parts:
            continue
        files.append(p)
    return sorted(files)


def prerender(dry_run: bool = False) -> int:
    import mermaidx

    files = _find_content_files()

    code_by_hash: dict[str, str] = {}
    for f in files:
        content = f.read_text(encoding="utf-8")
        for code in _find_mermaid_blocks(content):
            code_by_hash[_code_hash(code)] = code

    rendered = 0
    skipped = 0

    for h, code in code_by_hash.items():
        for theme_label, theme_name in THEMES:
            out = MERMAID_DIR / f"{h}-{theme_label}.svg"
            if out.exists():
                skipped += 1
                continue
            if not dry_run:
                out.parent.mkdir(parents=True, exist_ok=True)
                svg = mermaidx.render(code, theme=theme_name).svg()
                out.write_text(svg, encoding="utf-8")
            rendered += 1

    removed = 0
    if MERMAID_DIR.exists():
        for svg_file in MERMAID_DIR.glob("*.svg"):
            prefix = svg_file.stem.rsplit("-", 1)[0]
            if prefix not in code_by_hash:
                if not dry_run:
                    svg_file.unlink()
                removed += 1

    action = "Would " if dry_run else ""
    parts = [f"{action}rendered {rendered} SVGs", f"{skipped} already exist"]
    if removed:
        parts.append(f"{removed} stale removed")
    print(f"{parts[0]} ({', '.join(parts[1:])})")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true", help="show what would be rendered without writing")
    args = p.parse_args()
    return prerender(dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
