
import powerwalk

from blog_chat.core.config import CONTENT_DIR
from blog_chat.features.posts.parser import parse_markdown_file


def get_posts(lang: str | None = None) -> list[dict]:
    posts = []
    for entry in powerwalk.walk(CONTENT_DIR, filter="**/*.md"):
        post = parse_markdown_file(entry.path)
        if post and (lang is None or post.get("lang") == lang):
            posts.append(post)
    posts.sort(key=lambda p: p.get("slug", ""))
    return sorted(posts, key=lambda p: p.get("created", ""), reverse=True)


def get_post(slug: str, lang: str | None = None) -> dict | None:
    for entry in powerwalk.walk(CONTENT_DIR, filter="**/*.md"):
        post = parse_markdown_file(entry.path)
        if post and post.get("slug") == slug:
            if lang is None or post.get("lang") == lang:
                return post
            if not post.get("lang"):
                return post
    return None
