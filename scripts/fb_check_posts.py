#!/usr/bin/env python3
"""Heuristic check for scraped Facebook markdown files.

Identifies bad extractions: placeholder images, garbage text, missing content.

Usage:
    python scripts/fb_check_posts.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

DRAFTS_DIR = Path("content/_drafts/fb")
ASSETS_DIR = DRAFTS_DIR / "assets"

# Signals of a bad extraction
BAD_TITLE_PATTERNS = [
    r"^Christian Camacho (shared|updated|added)",
    r"^[A-Z][a-z]+ [A-Z][a-z]+ (shared|updated|added)",
    r"^Crow Systems",
    r"^Tijuana PC",
]

BAD_CONTENT_SIGNALS = [
    "See more",
    "All reactions:",
    "Like\nComment\nShare",
    "Reply\n",
    "View more comments",
    "Comment as ",
]


def check_post(filepath: Path) -> list[str]:
    """Return list of problems found in a post."""
    problems = []
    content = filepath.read_text(encoding="utf-8")

    # Extract frontmatter
    fm_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        problems.append("no_frontmatter")
        return problems

    fm = fm_match.group(1)
    title = re.search(r'title:\s*"([^"]*)"', fm)
    origin = re.search(r'origin_link:\s*"([^"]*)"', fm)
    title_text = title.group(1) if title else ""

    # Check title
    for pattern in BAD_TITLE_PATTERNS:
        if re.match(pattern, title_text):
            problems.append(f"title_is_action: {title_text[:50]}")
            break

    # Extract body (after frontmatter)
    body = content[fm_match.end():].strip()

    # Check body
    body_len = len(body)
    if body_len < 20:
        problems.append(f"body_too_short: {body_len} chars")

    # Check for video/photo URLs but missing media in markdown
    if origin:
        url = origin.group(1)
        has_video_url = "/videos/" in url
        has_photo_url = "/photo.php" in url or "/photo/" in url
        has_album_url = "/media/set/" in url
        has_video_tag = "<video" in body.lower()
        has_image_tag = "![" in body or "<img" in body.lower()

        if has_video_url and not has_video_tag:
            problems.append("missing_video: URL has /videos/ but no <video> in markdown")
        if has_photo_url and not has_image_tag:
            problems.append("missing_photo: URL has /photo but no image in markdown")
        if has_album_url and not has_image_tag:
            problems.append("missing_album_images: URL has /media/set but no images in markdown")

    # Check for comment noise
    comment_signals = sum(1 for s in BAD_CONTENT_SIGNALS if s in body)
    if comment_signals >= 2:
        problems.append(f"comment_noise: {comment_signals} signals")

    # Check for images that are placeholders (< 500 bytes)
    img_refs = re.findall(r"!\[.*?\]\(assets/(.*?)\)", body)
    for img_name in img_refs:
        img_path = ASSETS_DIR / img_name
        if img_path.exists():
            size = img_path.stat().st_size
            if size < 500:
                problems.append(f"placeholder_image: {img_name} ({size}b)")

    # Check for video posts (should have <video> tag)
    has_video = "<video" in body.lower()
    has_video_link = origin and "videos" in (origin.group(1) if origin else "")

    # Check if text is mostly metadata
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    meaningful_lines = [l for l in lines if not re.match(
        r"^(Shared with|Friends|Only me|Public|Specific friends|\d+[ymd]|"
        r"Christian Camacho|Crow Systems|Tijuana PC|·|Reply|Like|Comment|Share)$",
        l
    )]
    if len(meaningful_lines) < 2 and body_len > 10:
        problems.append("only_metadata")

    return problems


def main() -> int:
    if not DRAFTS_DIR.exists():
        print("No drafts directory found.")
        return 1

    files = sorted(DRAFTS_DIR.glob("*.md"))
    print(f"Checking {len(files)} posts...\n")

    good = 0
    bad_files = []

    for f in files:
        problems = check_post(f)
        if problems:
            bad_files.append((f.name, problems))
        else:
            good += 1

    print(f"Good: {good}/{len(files)}")
    print(f"Bad:  {len(bad_files)}/{len(files)}\n")

    if bad_files:
        print("=== Posts needing re-extraction ===\n")
        for name, probs in bad_files:
            print(f"  {name}")
            for p in probs:
                print(f"    - {p}")
            print()

    # Output bad file list for agent processing
    bad_list = DRAFTS_DIR / "_bad_posts.txt"
    with open(bad_list, "w") as f:
        for name, probs in bad_files:
            f.write(f"{name}\t{','.join(probs)}\n")
    print(f"Bad post list saved to {bad_list}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
