import re
from pathlib import Path

import markdown
import powerwalk
import yaml
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware

CONTENT_DIR = Path("content")


def parse_markdown_file(file_path: Path) -> dict | None:
    content = file_path.read_text(encoding="utf-8")
    
    frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    
    if frontmatter_match:
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
        body = content[frontmatter_match.end():]
    else:
        frontmatter = {}
        body = content
    
    return {
        "title": frontmatter.get("title", file_path.stem),
        "slug": frontmatter.get("slug", file_path.stem),
        "tags": frontmatter.get("tags", []),
        "created": frontmatter.get("created", ""),
        "updated": frontmatter.get("updated", ""),
        "content": body.strip(),
    }


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


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost"],
    allow_methods=["GET", "POST"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="src/blog_chat/templates")
templates.env.filters["markdown"] = lambda text: markdown.markdown(text or "")


@app.get("/")
def read_root(request: Request):
    posts = get_posts()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})


@app.get("/{slug}")
def read_item(request: Request, slug: str):
    post = get_post(slug)
    if not post:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "posts": get_posts(), "error": "Post not found"},
            status_code=404,
        )
    return templates.TemplateResponse("post.html", {"request": request, "post": post})
