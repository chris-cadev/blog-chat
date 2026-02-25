from pathlib import Path

from fastapi import APIRouter, Request
import markdown

from blog_chat.core.filters import add_markdown_filter
from blog_chat.core.responses import create_templates
from blog_chat.features.accounts.services import get_username_from_cookie
from blog_chat.features.posts.services import get_post, get_posts

router = APIRouter()

posts_template_dirs = [
    Path("src/blog_chat/features/posts/templates"),
    Path("src/blog_chat/features/chat/templates"),
]
templates = create_templates(posts_template_dirs)
add_markdown_filter(templates)


@router.get("/")
def read_root(request: Request):
    posts = get_posts()
    username = get_username_from_cookie(request)
    return templates.TemplateResponse(
        "index.html", {"request": request, "posts": posts,
                       "room": "offtopic", "username": username}
    )


@router.get("/{slug}")
def read_item(request: Request, slug: str):
    post = get_post(slug)
    username = get_username_from_cookie(request)
    if not post:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "posts": get_posts(), "error": "Post not found",
             "username": username},
            status_code=404,
        )
    return templates.TemplateResponse(
        "post.html", {"request": request, "post": post,
                      "room": slug, "username": username}
    )
