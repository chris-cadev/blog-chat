
import powerwalk

from blog_chat.core.config import CONTENT_DIR
from blog_chat.features.posts.parser import parse_markdown_file


def get_posts() -> list[dict]:
    posts = []
    for entry in powerwalk.walk(CONTENT_DIR, filter="**/*.md"):
        post = parse_markdown_file(entry.path)
        if post:
            posts.append(post)
    return sorted(posts, key=lambda p: p.get("created", ""), reverse=True)


def get_post(slug: str) -> dict | None:
    for entry in powerwalk.walk(CONTENT_DIR, filter="**/*.md"):
        post = parse_markdown_file(entry.path)
        if post and post.get("slug") == slug:
            return post
    return None
