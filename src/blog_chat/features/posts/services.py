
from pathlib import Path

import powerwalk

from blog_chat.core.config import APP_ENV, CONTENT_DIR
from blog_chat.features.posts.parser import parse_markdown_file

_IS_DEV = APP_ENV == "development"


def _is_draft(path: Path) -> bool:
    return "_drafts" in path.parts


def get_posts(lang: str | None = None) -> list[dict]:
    posts = []
    for entry in powerwalk.walk(CONTENT_DIR, filter="**/*.md"):
        if not _IS_DEV and _is_draft(entry.path):
            continue
        post = parse_markdown_file(entry.path)
        if post and (lang is None or post.get("lang") == lang):
            posts.append(post)
    return sorted(
        posts,
        key=lambda p: (
            str(p.get("created", "")),
            str(p.get("updated") or p.get("created", "")),
            p.get("title", "").lower(),
        ),
        reverse=True,
    )


def get_post(slug: str, lang: str | None = None) -> dict | None:
    for entry in powerwalk.walk(CONTENT_DIR, filter="**/*.md"):
        if not _IS_DEV and _is_draft(entry.path):
            continue
        post = parse_markdown_file(entry.path)
        if post and post.get("slug") == slug:
            if lang is None or post.get("lang") == lang:
                return post
            if not post.get("lang"):
                return post
    return None


def get_post_by_lang_group(lang_group: str, lang: str) -> dict | None:
    for entry in powerwalk.walk(CONTENT_DIR, filter="**/*.md"):
        if not _IS_DEV and _is_draft(entry.path):
            continue
        post = parse_markdown_file(entry.path)
        if post and post.get("lang_group") == lang_group and post.get("lang") == lang:
            return post
    return None


FB_DIR = CONTENT_DIR / "_drafts" / "fb"


def get_fb_post(slug: str) -> dict | None:
    for entry in powerwalk.walk(FB_DIR, filter="**/*.md"):
        post = parse_markdown_file(entry.path)
        if post and post.get("slug") == slug:
            return post
    return None


def get_fb_posts() -> list[dict]:
    posts = []
    for entry in powerwalk.walk(FB_DIR, filter="**/*.md"):
        post = parse_markdown_file(entry.path)
        if post:
            posts.append(post)
    return sorted(
        posts,
        key=lambda p: (
            str(p.get("created", "")),
            str(p.get("updated") or p.get("created", "")),
            p.get("title", "").lower(),
        ),
        reverse=True,
    )
