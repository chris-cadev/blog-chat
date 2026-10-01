import json

from markupsafe import Markup

from blog_chat.core.config import SITE_URL

SITE_NAME = "Chrislabs Blog"
AUTHOR_NAME = "Chris Camacho"
AUTHOR_EMAIL = "chris@chrislabs.net"
GITHUB_PROFILE = "https://github.com/chris-cadev"
GITHUB_REPO = "https://github.com/chris-cadev/blog-chat"


def organization_schema() -> dict:
    return {
        "@type": "Organization",
        "name": "Chrislabs",
        "url": SITE_URL,
        "sameAs": [GITHUB_REPO],
    }


def website_schema() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": SITE_URL,
        "inLanguage": ["en", "es", "fr"],
        "publisher": organization_schema(),
    }


def person_schema(lang: str = "en") -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": AUTHOR_NAME,
        "email": f"mailto:{AUTHOR_EMAIL}",
        "url": f"{SITE_URL}/{lang}/about",
        "sameAs": [GITHUB_PROFILE, GITHUB_REPO],
        "worksFor": organization_schema(),
    }


def article_schema(post: dict, site_url: str = SITE_URL) -> dict:
    lang = post.get("lang") or "en"
    slug = post.get("slug") or ""
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post.get("title") or slug,
        "inLanguage": lang,
        "mainEntityOfPage": f"{site_url}/{lang}/{slug}",
        "author": {
            "@type": "Person",
            "name": AUTHOR_NAME,
            "url": f"{site_url}/{lang}/about",
        },
        "publisher": organization_schema(),
    }
    description = (post.get("description") or "").strip()
    if description:
        data["description"] = description[:300]
    if post.get("created"):
        data["datePublished"] = post["created"]
    modified = post.get("updated") or post.get("created")
    if modified:
        data["dateModified"] = modified
    return data


def to_jsonld(data: dict) -> Markup:
    return Markup(json.dumps(data, ensure_ascii=False))


def build_llms_txt(posts: list[dict], site_url: str = SITE_URL) -> str:
    by_lang: dict[str, list[dict]] = {}
    for post in posts:
        lang = post.get("lang") or "mixed"
        by_lang.setdefault(lang, []).append(post)

    lines = [
        f"# {SITE_NAME}",
        "",
        "> Personal blog on software, life, and the things in between. Posts in English and Spanish.",
        "",
        f"Main site: {site_url}",
        f"Sitemap: {site_url}/sitemap.xml",
        f"About the author: {site_url}/en/about",
        "",
    ]
    labels = {"en": "English", "es": "Español", "fr": "Français", "mixed": "Other"}
    for lang in ("en", "es", "fr", "mixed"):
        items = by_lang.get(lang)
        if not items:
            continue
        lines.append(f"## {labels[lang]}")
        lines.append("")
        for post in items:
            page_lang = post.get("lang") or "en"
            url = f"{site_url}/{page_lang}/{post['slug']}"
            title = post.get("title") or post["slug"]
            desc = (post.get("description") or "").replace("\n", " ").strip()
            if desc:
                lines.append(f"- [{title}]({url}): {desc}")
            else:
                lines.append(f"- [{title}]({url})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
