from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, Response

from blog_chat.core.filters import add_markdown_filter
from blog_chat.core.responses import create_templates
from blog_chat.core.config import SITE_URL
from blog_chat.features.accounts.services import get_username_from_cookie
from blog_chat.features.posts.services import get_post, get_posts

router = APIRouter()

posts_template_dirs = [
    Path("src/blog_chat/features/posts/templates"),
    Path("src/blog_chat/features/chat/templates"),
]
templates = create_templates(posts_template_dirs)
add_markdown_filter(templates)


@router.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    return f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""


@router.get("/sitemap.xml", response_class=Response)
def sitemap(request: Request):
    posts = get_posts()
    urls = []
    for post in posts:
        date = post.get("updated") or post.get(
            "created") or datetime.now().isoformat()
        urls.append(f"""  <url>
    <loc>{SITE_URL}/{post['slug']}</loc>
    <lastmod>{date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{SITE_URL}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
{chr(10).join(urls)}
</urlset>"""
    return Response(content=sitemap_xml, media_type="application/xml")


@router.get("/")
def read_root(request: Request):
    posts = get_posts()
    username = get_username_from_cookie(request)
    return templates.TemplateResponse(
        "index.html", {"request": request, "posts": posts,
                       "room": "offtopic", "username": username}
    )


@router.get("/{slug:path}")
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
