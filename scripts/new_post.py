#!/usr/bin/env python3
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

CONTENT_DIR = Path("content")
DRAFTS_DIR = CONTENT_DIR / "_drafts"


def create_draft(title: str = "", now: datetime | None = None, drafts_dir: Path = DRAFTS_DIR) -> Path:
    now = now or datetime.now()
    base = drafts_dir / now.strftime("%Y-%m-%d-%H%M.md")
    path, n = base, 2
    while path.exists():
        path = drafts_dir / f"{now.strftime('%Y-%m-%d-%H%M')}-{n}.md"
        n += 1
    date = now.strftime("%Y-%m-%d")
    frontmatter = yaml.safe_dump(
        {"title": title, "created": date, "updated": date},
        sort_keys=False,
        allow_unicode=True,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}---\n\n", encoding="utf-8")
    return path


def open_editor(path: Path) -> str | None:
    for editor in ("nvim", "code"):
        if shutil.which(editor):
            subprocess.call([editor, str(path)])
            return editor
    print(f"No editor found (nvim/code). Draft created at {path}")
    return None


def main(argv: list[str]) -> int:
    title = " ".join(argv[1:]).strip()
    path = create_draft(title)
    print(f"Draft created at {path}")
    open_editor(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))