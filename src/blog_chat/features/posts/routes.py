from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, Response, RedirectResponse

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

LANGS = ("en", "es", "fr")
LANG_COOKIE = "lang"
LANG_COOKIE_MAX_AGE = 60 * 60 * 24 * 365

TRANSLATIONS = {
    "en": {
        "home": "Home",
        "back_to_posts": "Back to all posts",
        "posts_title": "Blog Posts",
        "no_posts": "No posts found.",
        "posts_tagged": "Posts tagged",
        "chat_title": "Off-topic",
        "enter_name": "Enter your name",
        "join": "Join",
        "logged_in_as": "Logged in as",
        "change_username": "Change username",
        "type_message": "Type a message... (Enter to send)",
        "send": "Send",
        "no_messages": "No messages yet. Start the conversation!",
        "language_not_found": "Language not found",
        "post_not_found": "Post not found",
    },
    "es": {
        "home": "Inicio",
        "back_to_posts": "Volver a todos los artículos",
        "posts_title": "Artículos del blog",
        "no_posts": "No se encontraron artículos.",
        "posts_tagged": "Artículos etiquetados",
        "chat_title": "Off-topic",
        "enter_name": "Escribe tu nombre",
        "join": "Unirse",
        "logged_in_as": "Conectado como",
        "change_username": "Cambiar nombre",
        "type_message": "Escribe un mensaje... (Enter para enviar)",
        "send": "Enviar",
        "no_messages": "Aún no hay mensajes. ¡Inicia la conversación!",
        "language_not_found": "Idioma no encontrado",
        "post_not_found": "Artículo no encontrado",
    },
    "fr": {
        "home": "Accueil",
        "back_to_posts": "Retour à tous les articles",
        "posts_title": "Articles du blog",
        "no_posts": "Aucun article trouvé.",
        "posts_tagged": "Articles tagués",
        "chat_title": "Off-topic",
        "enter_name": "Saisissez votre nom",
        "join": "Rejoindre",
        "logged_in_as": "Connecté en tant que",
        "change_username": "Changer de nom",
        "type_message": "Écrivez un message... (Entrée pour envoyer)",
        "send": "Envoyer",
        "no_messages": "Aucun message pour l'instant. Lancez la conversation !",
        "language_not_found": "Langue introuvable",
        "post_not_found": "Article introuvable",
    },
}


def _make_t(lang: str | None):
    table = TRANSLATIONS.get(lang or "en", TRANSLATIONS["en"])

    def translate(key: str) -> str:
        return table.get(key, key)

    return translate


def _language_switcher(request: Request, lang: str | None, slug: str | None) -> list[dict]:
    return [
        {
            "code": code,
            "active": code == lang,
            "href": f"/{code}/{slug}" if slug else f"/{code}/",
        }
        for code in LANGS
    ]


def _preferred_lang(request: Request) -> str:
    cookie = request.cookies.get(LANG_COOKIE)
    if cookie in LANGS:
        return cookie
    entries = []
    accept = request.headers.get("accept-language", "")
    for part in accept.split(","):
        segments = [s.strip() for s in part.split(";")]
        code = segments[0].lower()
        q = 1.0
        for segment in segments[1:]:
            if segment.startswith("q="):
                try:
                    q = float(segment[2:])
                except ValueError:
                    q = 0.0
        entries.append((q, code))
    entries.sort(key=lambda item: item[0], reverse=True)
    for _, code in entries:
        base = code.split("-")[0]
        if base in LANGS:
            return base
    return "en"


def _with_lang_cookie(response: Response, lang: str) -> Response:
    response.set_cookie(
        LANG_COOKIE,
        lang,
        max_age=LANG_COOKIE_MAX_AGE,
        path="/",
        samesite="lax",
        httponly=True,
    )
    return response


def _context(request: Request, lang: str | None, **extra) -> dict:
    ctx = {"request": request, "lang": lang, "t": _make_t(lang)}
    ctx.update(extra)
    return ctx


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
        lang = post.get("lang") or "en"
        date = post.get("updated") or post.get(
            "created") or datetime.now().isoformat()
        urls.append(f"""  <url>
    <loc>{SITE_URL}/{lang}/{post['slug']}</loc>
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
    lang = _preferred_lang(request)
    return RedirectResponse(f"/{lang}/", status_code=302)


@router.get("/{lang}/")
def read_lang_index(request: Request, lang: str):
    if lang not in LANGS:
        return templates.TemplateResponse(
            "index.html",
            _context(request, "en", posts=get_posts(), error=_make_t("en")("language_not_found"),
                     username=get_username_from_cookie(request),
                     slug=None,
                     language_switcher=_language_switcher(request, None, None)),
            status_code=404,
        )
    posts = get_posts(lang)
    username = get_username_from_cookie(request)
    return _with_lang_cookie(
        templates.TemplateResponse(
            "index.html",
            _context(request, lang, posts=posts,
                     room="offtopic", username=username,
                     slug=None,
                     language_switcher=_language_switcher(request, lang, None)),
        ),
        lang,
    )


@router.get("/tags/{tag}")
def read_tag_redirect(request: Request, tag: str):
    return RedirectResponse(f"/{_preferred_lang(request)}/tags/{tag}")


@router.get("/{lang}/tags/{tag}")
def read_tag(request: Request, lang: str, tag: str):
    if lang not in LANGS:
        return RedirectResponse(f"/{_preferred_lang(request)}/tags/{tag}")
    posts = [p for p in get_posts(lang) if tag in (p.get("tags") or [])]
    username = get_username_from_cookie(request)
    return _with_lang_cookie(
        templates.TemplateResponse(
            "index.html",
            _context(request, lang, posts=posts, tag=tag,
                     room="offtopic", username=username,
                     slug=None,
                     language_switcher=_language_switcher(request, lang, None)),
        ),
        lang,
    )


@router.get("/{lang}/{slug:path}")
def read_item(request: Request, lang: str, slug: str):
    if lang not in LANGS:
        legacy = get_post(f"{lang}/{slug}")
        if legacy:
            legacy_lang = legacy.get("lang") or "en"
            return _with_lang_cookie(
                templates.TemplateResponse(
                    "post.html",
                    _context(request, legacy_lang, post=legacy,
                             room=legacy.get("slug"),
                             username=get_username_from_cookie(request),
                             slug=legacy.get("slug"),
                             language_switcher=_language_switcher(request, legacy_lang, legacy.get("slug"))),
                ),
                legacy_lang,
            )
        return templates.TemplateResponse(
            "index.html",
            _context(request, "en", posts=get_posts(), error=_make_t("en")("post_not_found"),
                     username=get_username_from_cookie(request),
                     slug=None,
                     language_switcher=_language_switcher(request, None, None)),
            status_code=404,
        )
    post = get_post(slug, lang)
    username = get_username_from_cookie(request)
    if not post:
        return _with_lang_cookie(
            templates.TemplateResponse(
                "index.html",
                _context(request, lang, posts=get_posts(lang), error=_make_t(lang)("post_not_found"),
                         username=username, slug=slug,
                         language_switcher=_language_switcher(request, lang, slug)),
                status_code=404,
            ),
            lang,
        )
    return _with_lang_cookie(
        templates.TemplateResponse(
            "post.html",
            _context(request, lang, post=post,
                     room=slug, username=username,
                     slug=slug,
                     language_switcher=_language_switcher(request, lang, slug)),
        ),
        lang,
    )
