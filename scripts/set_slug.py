#!/usr/bin/env python3
import re
import sys
from pathlib import Path

import yaml

CONTENT_DIR = Path("content")
LANGS = ("en", "es", "fr")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def assign_slug(draft_path: Path, slug: str, lang: str, content_dir: Path = CONTENT_DIR) -> Path:
    text = draft_path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"No frontmatter found in {draft_path}")
    frontmatter = yaml.safe_load(match.group(1)) or {}
    body = text[match.end():]

    for key, expected in (("slug", slug), ("lang", lang)):
        existing = frontmatter.get(key)
        if existing not in (None, expected):
            raise ValueError(
                f"{draft_path}: {key} already set to {existing!r}, refusing to overwrite with {expected!r}"
            )

    frontmatter["slug"] = slug
    frontmatter["lang"] = lang
    frontmatter["lang_group"] = slug

    target = content_dir / lang / f"{slug}.md"
    if target.exists() and target.resolve() != draft_path.resolve():
        raise ValueError(f"{target} already exists — slug {slug!r} already in use")
    target.parent.mkdir(parents=True, exist_ok=True)
    draft_path.replace(target)

    new_text = (
        "---\n"
        + yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True)
        + "---\n"
        + body
    )
    target.write_text(new_text, encoding="utf-8")
    return target


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(f"usage: {argv[0]} <draft.md> <slug> <lang>", file=sys.stderr)
        return 1
    _, draft, slug, lang = argv
    if not SLUG_RE.match(slug):
        print(f"error: slug must be kebab-case, got {slug!r}", file=sys.stderr)
        return 1
    if lang not in LANGS:
        print(f"error: lang must be one of {', '.join(LANGS)}, got {lang!r}", file=sys.stderr)
        return 1
    try:
        target = assign_slug(Path(draft), slug, lang)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Moved to {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))