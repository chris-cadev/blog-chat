#!/usr/bin/env python3
"""Migrate blog posts from chris-cadev/blog into blog-chat's content/.

Implements PRD-00001 (docs/plans/PRD-00001-gather-past-posts.md).
Source is the Hugo/trilingual debugchris blog; target is blog-chat's
flat markdown content/ directory consumed by features/posts.

Usage:
    python scripts/migrate_posts.py [--source /path/to/blog-repo] [--dry-run]

Behavior:
    - Copies content/logs, content/posts, content/pre posts as flat files.
    - Converts Hugo front matter to blog-chat fields (title, slug, tags,
      created, updated, description).
    - One post per language with a <stem>-<lang> slug; adds lang + lang_group.
    - Resolves Hugo shortcodes (meaning, yt-video, external-url, frame).
    - Rewrites cross-post markdown links and local image references.
    - Copies referenced images into src/assets/posts/<base> for vite to
      publish under /static/posts/.
    - Writes a migration report flagging drafts and edge cases.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import unicodedata
from pathlib import Path

import yaml

SOURCE_CONTENT = "content"
TARGET_CONTENT = Path("content")
TARGET_ASSETS = Path("src/assets/posts")

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

LANGS = ("en", "es", "fr")
LANG_EXT_RE = re.compile(r"\.(en|es|fr)\.md$")
HIDDEN_LANG_RE = re.compile(r"\.(en|es|fr)\.")

SHORTCODE_RE = re.compile(r"\{\{<\s*([a-z-]+)\s+([^>]*?)\s*>\}\}")
CROSS_LINK_RE = re.compile(r"\]\(([^()]+\.(?:en|es|fr)\.md)\)")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^()]+)\)")


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFC", text).strip().lower()
    text = re.sub(r"[^a-z0-9\u00e0-\u00ff]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text


def split_lang(filename: str) -> tuple[str, str | None]:
    match = LANG_EXT_RE.search(filename)
    if match:
        return filename[: match.start()], match.group(1)
    hidden = HIDDEN_LANG_RE.search(filename)
    if hidden:
        return filename[: hidden.start()], hidden.group(1)
    return filename[: -len(".md")] if filename.endswith(".md") else filename, None


def parse_front_matter(content: str) -> tuple[dict, str]:
    match = FRONT_MATTER_RE.match(content)
    if match:
        raw = match.group(1)
        front = {}
        if raw.strip():
            parsed = yaml.safe_load(raw)
            if isinstance(parsed, dict):
                front = parsed
        return front, content[match.end():]
    if content.startswith("---\n---\n"):
        return {}, content[len("---\n---\n"):]
    return {}, content


def yaml_scalar(value) -> str:
    out = yaml.safe_dump(value, default_flow_style=False, allow_unicode=True)
    if out.endswith("\n...\n"):
        out = out[:-4]
    return out.strip()


def dump_front_matter(front: dict) -> str:
    lines = ["---"]
    for key, value in front.items():
        if isinstance(value, str):
            lines.append(f"{key}: {yaml_scalar(value)}")
        elif isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {yaml_scalar(item)}" if isinstance(item, str) else f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def to_iso_date(value) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, str):
        match = re.search(r"\d{4}-\d{2}-\d{2}", value.strip())
        return match.group(0) if match else None
    return str(value)


def resolve_yt_id(src: str) -> str | None:
    if "youtube.com" in src:
        if "v=" in src:
            return src.split("v=")[1].split("&")[0]
        if "embed/" in src:
            return src.split("embed/")[1].split("/")[0]
    if "youtu.be" in src:
        return src.split("youtu.be/")[1].split("?")[0]
    if src and "/" not in src and " " not in src:
        return src
    return None


def convert_shortcode(name: str, args: dict[str, str]) -> str:
    if name == "meaning":
        word = args.get("word", "")
        return f"<em>{word}</em>"
    if name == "external-url":
        href = args.get("href", "")
        label = args.get("label") or href
        return f"[{label}]({href})"
    if name == "frame":
        src = args.get("src", "")
        return (
            f'<iframe loading="lazy" src="{src}" title="Embedded content" '
            f'style="width:100%; height:500px; border:0; border-radius:4px;"></iframe>'
        )
    if name == "yt-video":
        yt_id = resolve_yt_id(args.get("src", ""))
        if not yt_id:
            return f"{{{{< yt-video {' '.join(f'{k}={v!r}' for k, v in args.items())} >}}}}"
        return (
            '<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">'
            f'<iframe src="https://www.youtube.com/embed/{yt_id}" '
            'style="position: absolute; top:0; left:0; width:100%; height:100%; border:0;" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
            'allowfullscreen></iframe></div>'
        )
    return None


def resolve_shortcodes(body: str, report: list[str], file: Path) -> str:
    def repl(match: re.Match) -> str:
        name = match.group(1)
        args = dict(re.findall(r'(\w+)=["\']([^"\']*)["\']', match.group(2)))
        converted = convert_shortcode(name, args)
        if converted is None:
            report.append(f"UNKNOWN SHORTCODE: {file}: {match.group(0)}")
            return match.group(0)
        return converted

    return SHORTCODE_RE.sub(repl, body)


def collect_source_files(source: Path) -> list[Path]:
    files = []
    for section in ("logs", "posts", "pre"):
        base = source / SOURCE_CONTENT / section
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            if path.name.startswith("_"):
                continue
            files.append(path)
    return files


def base_stem_for(file: Path, section: str) -> str:
    if file.parent.name == section:
        return file.stem
    return file.parent.name


def migrate(source: Path, dry_run: bool) -> Path:
    report: list[str] = []
    files = collect_source_files(source)
    report.append(f"SOURCE FILES FOUND: {len(files)}")
    report.append("")

    created_slugs: set[tuple[str, str]] = set()
    migrated: list[tuple[Path, str]] = []

    for file in files:
        section = file.parent.name if file.parent.name in ("logs", "posts", "pre") else "posts"
        if file.parent.name not in ("logs", "posts", "pre"):
            section = "posts"
        raw_stem, lang = split_lang(file.name)
        base = slugify(base_stem_for(file, section)) if raw_stem == "index" else slugify(raw_stem)
        if not base:
            base = slugify(file.stem)

        content = file.read_text(encoding="utf-8")
        front, body = parse_front_matter(content)

        # Language: extension wins; else translated-from; else None.
        if lang is None:
            lang = front.get("translated-from") if isinstance(front.get("translated-from"), str) else None
        if lang and lang not in LANGS:
            lang = None

        slug = base
        dup_key = (lang or "mixed", base)
        if dup_key in created_slugs:
            report.append(f"DUPLICATE SLUG: {slug} ({file})")
        created_slugs.add(dup_key)

        is_draft = bool(front.get("draft"))
        if is_draft:
            report.append(f"DRAFT: {slug} ({file})")

        # Front matter mapping.
        created = to_iso_date(front.get("date")) or to_iso_date(front.get("created"))
        updated = to_iso_date(front.get("updated")) or created
        description = front.get("description")
        if isinstance(description, list):
            description = " ".join(str(d) for d in description if d)
        if description in (None, ""):
            description = front.get("more")
        if isinstance(description, list):
            description = " ".join(str(d) for d in description if d)

        new_front: dict = {}
        if front.get("title"):
            new_front["title"] = str(front.get("title"))
        if slug:
            new_front["slug"] = slug
        if isinstance(front.get("tags"), list) and front["tags"]:
            new_front["tags"] = [str(t) for t in front["tags"]]
        if created:
            new_front["created"] = created
        if updated:
            new_front["updated"] = updated
        if description:
            new_front["description"] = str(description)
        if lang:
            new_front["lang"] = lang
        if base:
            new_front["lang_group"] = base

        # Resolve shortcodes.
        body = resolve_shortcodes(body, report, file)

        # Rewrite cross-post links to target slugs.
        def link_repl(match: re.Match) -> str:
            target = match.group(1)
            target_base, target_lang = split_lang(target)
            target_slug = slugify(target_base)
            return f"](/{target_lang or lang or 'en'}/{target_slug})"

        body = CROSS_LINK_RE.sub(link_repl, body)

        # Images: rewrite refs and copy files.
        def image_repl(match: re.Match) -> str:
            alt, ref = match.group(1), match.group(2)
            if ref.startswith(("http://", "https://", "/")):
                return match.group(0)
            name = ref.split("/")[-1]
            src_img = file.parent / name
            if not src_img.exists():
                report.append(f"MISSING IMAGE: {file}: {ref}")
                return match.group(0)
            return f"![{alt}](/static/posts/{name})"

        body = IMAGE_RE.sub(image_repl, body)

        output = dump_front_matter(new_front) + body + "\n"
        lang_dir = lang if lang else "mixed"
        target_path = TARGET_CONTENT / lang_dir / f"{base}.md"
        migrated.append((target_path, slug))

        if dry_run:
            print(f"[dry-run] {file} -> {target_path}")
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(output, encoding="utf-8")

    # Copy images referenced in source post folders (deduped by name).
    copied_images: set[Path] = set()
    for file in files:
        for img in file.parent.glob("*"):
            if img.is_file() and img.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
                if img in copied_images:
                    continue
                copied_images.add(img)
                dest = TARGET_ASSETS / img.name
                if dry_run:
                    print(f"[dry-run] copy {img} -> {dest}")
                else:
                    TARGET_ASSETS.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(img, dest)

    report_path = Path("migration_report.txt")
    if not dry_run:
        report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    else:
        print("\n".join(report))
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("/tmp/opencode/blog-src"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.source.exists():
        print(f"Source repo not found at {args.source}. Clone it first:", file=sys.stderr)
        print("  gh repo clone chris-cadev/blog /tmp/opencode/blog-src", file=sys.stderr)
        return 1

    report_path = migrate(args.source, dry_run=args.dry_run)
    print(f"\nReport written to {report_path}" if not args.dry_run else "\nDry-run complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
