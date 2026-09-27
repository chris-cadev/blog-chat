#!/usr/bin/env python3
"""Clean up Facebook draft posts based on analysis report.

Moves posts recommended for deletion to content/_drafts/fb/_trash/.
Keeps associated assets with the post.

Usage:
    python scripts/fb_cleanup.py              # dry-run (preview)
    python scripts/fb_cleanup.py --apply      # actually move files
    python scripts/fb_cleanup.py --score 3.0  # delete posts below this score
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

DRAFTS_DIR = Path("content/_drafts/fb")
TRASH_DIR = DRAFTS_DIR / "_trash"
REPORT_FILE = DRAFTS_DIR / "_analysis_report.json"


def move_to_trash(filepath: Path, trash_dir: Path) -> Path:
    """Move a file to trash, preserving filename."""
    trash_dir.mkdir(exist_ok=True)
    dest = trash_dir / filepath.name
    # Handle name collision
    if dest.exists():
        stem = filepath.stem
        suffix = filepath.suffix
        i = 1
        while dest.exists():
            dest = trash_dir / f"{stem}_{i}{suffix}"
            i += 1
    shutil.move(str(filepath), str(dest))
    return dest


def main() -> int:
    dry_run = "--apply" not in sys.argv
    threshold = 7.5  # default: delete posts with score < 7.5

    # Parse custom threshold
    for i, arg in enumerate(sys.argv):
        if arg == "--score" and i + 1 < len(sys.argv):
            threshold = float(sys.argv[i + 1])

    if not REPORT_FILE.exists():
        print(f"Error: {REPORT_FILE} not found. Run fb_analyze.py first.")
        return 1

    report = json.loads(REPORT_FILE.read_text(encoding="utf-8"))
    posts = report["posts"]

    to_delete = [p for p in posts if p["score"] < threshold]
    to_keep = [p for p in posts if p["score"] >= threshold]

    print(f"Threshold: score < {threshold}")
    print(f"Posts to delete: {len(to_delete)}")
    print(f"Posts to keep: {len(to_keep)}")
    print()

    if dry_run:
        print("DRY RUN — no files will be moved\n")

    moved = 0
    assets_moved = 0

    for p in to_delete:
        filepath = DRAFTS_DIR / p["filename"]
        if not filepath.exists():
            print(f"  SKIP (not found): {p['filename']}")
            continue

        # Check for associated assets (images/videos)
        stem = filepath.stem
        asset_files = list(DRAFTS_DIR.glob(f"assets/{stem}_*"))

        if dry_run:
            print(f"  DELETE: [{p['score']:4.1f}] {p['title'][:55]}")
            print(f"          {p['filename']}")
            if asset_files:
                print(f"          + {len(asset_files)} assets")
        else:
            move_to_trash(filepath, TRASH_DIR)
            moved += 1
            for asset in asset_files:
                move_to_trash(asset, TRASH_DIR / "assets")
                assets_moved += 1

    print()
    if dry_run:
        print("To apply, run: python scripts/fb_cleanup.py --apply")
    else:
        print(f"Moved {moved} posts and {assets_moved} assets to {TRASH_DIR}")

    # Summary of what stays
    print(f"\n{'=' * 60}")
    print(f"QUEDAN {len(to_keep)} POSTS EN content/_drafts/fb/")
    print(f"{'=' * 60}")
    cats: dict[str, int] = {}
    for p in to_keep:
        cats[p["category"]] = cats.get(p["category"], 0) + 1
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat:20s} {count:3d}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
