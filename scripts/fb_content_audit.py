#!/usr/bin/env python3
"""Audit all Facebook draft posts for extraction quality issues.

Scans content/_drafts/fb/*.md and reports which posts need re-extraction.

Usage:
    python scripts/fb_content_audit.py
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

DRAFTS_DIR = Path("content/_drafts/fb")
REPORT_FILE = DRAFTS_DIR / "_audit_report.json"
RESCRAPE_FILE = DRAFTS_DIR / "_rescrape_list.json"

TITLE_ACTION_RE = re.compile(
    r"^(Christian Camacho|You|Crow Systems|Tijuana PC|Facebook)"
    r" (shared|updated|added|created)\b"
)

DIALOG_GARBAGE_PREFIXES = ("Notifications", "Menu", "AllUnread", "See allUnread")
COMMENT_NOISE_RE = re.compile(r"Comment as ", re.IGNORECASE)


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_text)."""
    match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}, content
    fm = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            fm[key.strip()] = val.strip().strip('"')
    return fm, content[match.end():].strip()


def strip_media(body: str) -> str:
    """Remove image/video/link markdown, return plain text only."""
    text = re.sub(r"!\[.*?\]\(.*?\)", "", body)
    text = re.sub(r"<video[^>]*>.*?</video>", "", text, flags=re.DOTALL)
    text = re.sub(r"<iframe[^>]*>.*?</iframe>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def check_post(filepath: Path) -> dict:
    """Check a single post, return {filename, issues, origin_url}."""
    content = filepath.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)
    title = fm.get("title", "")
    origin_url = fm.get("origin_link", "")
    issues = []

    # 1. body_has_facebook_noise
    facebook_count = body.lower().count("facebook")
    if facebook_count >= 5:
        issues.append("body_has_facebook_noise")

    # 2. body_has_dialog_garbage
    body_stripped = body.lstrip()
    if any(body_stripped.startswith(p) for p in DIALOG_GARBAGE_PREFIXES):
        issues.append("body_has_dialog_garbage")

    # 3. body_has_comment_noise — "Comment as" in first half
    half = len(body) // 2
    if COMMENT_NOISE_RE.search(body[:half]):
        issues.append("body_has_comment_noise")

    # 4. title_is_action
    if TITLE_ACTION_RE.match(title):
        issues.append("title_is_action")

    # 5. description_is_noise
    desc = fm.get("description", "")
    if any(desc.startswith(p) for p in DIALOG_GARBAGE_PREFIXES):
        issues.append("description_is_noise")

    # 6. body_is_short — text-only < 10 chars but has media
    text_only = strip_media(body)
    has_media = "![" in body or "<video" in body.lower() or "<iframe" in body.lower()
    if len(text_only) < 10 and has_media:
        issues.append("body_is_short")

    # 7. missing_media
    if origin_url:
        if "/videos/" in origin_url and "<video" not in body.lower():
            issues.append("missing_media")
        elif ("/photo.php" in origin_url or "/photo/" in origin_url) and "![" not in body:
            issues.append("missing_media")
        elif "/media/set/" in origin_url and "![" not in body:
            issues.append("missing_media")

    # 8. body_has_repeated_line
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    line_counts = defaultdict(int)
    for line in lines:
        line_counts[line] += 1
    for line, count in line_counts.items():
        if count >= 3:
            issues.append("body_has_repeated_line")
            break

    return {
        "filename": filepath.name,
        "issues": issues,
        "origin_url": origin_url,
    }


def main() -> int:
    files = sorted(DRAFTS_DIR.glob("*.md"))
    print(f"Scanning {len(files)} posts in {DRAFTS_DIR}")

    results = []
    issues_by_type = defaultdict(int)
    rescrape = []

    for f in files:
        result = check_post(f)
        results.append(result)
        for issue in result["issues"]:
            issues_by_type[issue] += 1
        # Re-scrape if body has facebook noise or dialog garbage
        if any(i in result["issues"] for i in ("body_has_facebook_noise", "body_has_dialog_garbage")):
            rescrape.append(result["filename"])

    affected = [r for r in results if r["issues"]]

    report = {
        "total_posts": len(files),
        "issues_by_type": dict(issues_by_type),
        "affected_posts": affected,
    }

    REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    RESCRAPE_FILE.write_text(json.dumps(rescrape, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nTotal: {len(files)} posts, {len(affected)} with issues")
    print(f"Re-scrape needed: {len(rescrape)} posts\n")

    print("Issues by type:")
    for issue, count in sorted(issues_by_type.items(), key=lambda x: -x[1]):
        print(f"  {issue}: {count}")

    print(f"\nReport: {REPORT_FILE}")
    print(f"Re-scrape list: {RESCRAPE_FILE}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
