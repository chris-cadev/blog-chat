from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, Response, RedirectResponse

from blog_chat.core.filters import add_filter, add_markdown_filter
from blog_chat.core.responses import create_templates
from blog_chat.core.config import SITE_URL
from blog_chat.features.accounts.services import (
    create_token,
    generate_guest_name,
    get_username_from_cookie,
)
from blog_chat.features.chat.routes import get_username_color
from blog_chat.features.posts.services import get_post, get_posts

router = APIRouter()

posts_template_dirs = [
    Path("src/blog_chat/features/posts/templates"),
    Path("src/blog_chat/features/chat/templates"),
]
templates = create_templates(posts_template_dirs)
add_markdown_filter(templates)
add_filter(templates, "username_color", get_username_color)

LANGS = ("en", "es", "fr")
LANG_FLAGS = {"en": "🇺🇸", "es": "🇲🇽", "fr": "🇫🇷"}
LANG_NAMES = {"en": "English", "es": "Español", "fr": "Français"}
LANG_COOKIE = "lang"
LANG_COOKIE_MAX_AGE = 60 * 60 * 24 * 365
CHAT_TOKEN_COOKIE = "chat_token"
CHAT_TOKEN_MAX_AGE = 60 * 60 * 24 * 30

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
        "type_message": "Type a message…",
        "enter_to_send": "Press Enter to send",
        "send": "Send",
        "no_messages": "No messages yet. Start the conversation!",
        "starter_say_hi": "Say hi 👋",
        "starter_take": "What's your take?",
        "starter_ask": "Ask about this post",
        "starter_share": "Share a thought",
        "starter_reading": "What are you reading?",
        "starter_say_hi_message": "Hi! 👋",
        "starter_take_message": "I'd love to hear your take on this.",
        "starter_ask_message": "What do you think about this post?",
        "starter_share_message": "I'd like to share a thought.",
        "starter_reading_message": "What are you reading right now?",
        "language_not_found": "Language not found",
        "post_not_found": "Post not found",
    },
    "es": {
        "home": "Inicio",
        "back_to_posts": "Volver a todos los artículos",
        "posts_title": "Posts",
        "no_posts": "No se encontraron artículos.",
        "posts_tagged": "Posts etiquetados",
        "chat_title": "Off-topic",
        "enter_name": "Escribe tu nombre",
        "join": "Unirse",
        "logged_in_as": "Conectado como",
        "change_username": "Cambiar nombre",
        "type_message": "Escribe un mensaje…",
        "enter_to_send": "Enter para enviar",
        "send": "Enviar",
        "no_messages": "Aún no hay mensajes. ¡Inicia la conversación!",
        "starter_say_hi": "¡Hola! 👋",
        "starter_take": "¿Qué opinas?",
        "starter_ask": "Pregunta sobre este artículo",
        "starter_share": "Comparte una idea",
        "starter_reading": "¿Qué estás leyendo?",
        "starter_say_hi_message": "¡Hola! 👋",
        "starter_take_message": "Me encantaría saber tu opinión.",
        "starter_ask_message": "¿Qué opinas de este artículo?",
        "starter_share_message": "Me gustaría compartir una idea.",
        "starter_reading_message": "¿Qué estás leyendo ahora?",
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
        "type_message": "Écrivez un message…",
        "enter_to_send": "Entrée pour envoyer",
        "send": "Envoyer",
        "no_messages": "Aucun message pour l'instant. Lancez la conversation !",
        "starter_say_hi": "Dis bonjour 👋",
        "starter_take": "Qu'en pensez-vous ?",
        "starter_ask": "Posez une question sur cet article",
        "starter_share": "Partagez une idée",
        "starter_reading": "Que lisez-vous ?",
        "starter_say_hi_message": "Bonjour ! 👋",
        "starter_take_message": "J'aimerais bien connaître votre avis.",
        "starter_ask_message": "Que pensez-vous de cet article ?",
        "starter_share_message": "J'aimerais partager une idée.",
        "starter_reading_message": "Que lisez-vous en ce moment ?",
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
            "flag": LANG_FLAGS[code],
            "title": LANG_NAMES[code],
        }
        for code in LANGS
        if code != lang
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


def _render(
    template_name: str,
    request: Request,
    lang: str | None,
    status_code: int | None = None,
    apply_lang_cookie: bool = True,
    **extra,
) -> Response:
    username = get_username_from_cookie(request)
    generated = username is None
    if generated:
        username = generate_guest_name()
    extra["username"] = username

    template_kwargs = {}
    if status_code is not None:
        template_kwargs["status_code"] = status_code
    response = templates.TemplateResponse(
        template_name,
        _context(request, lang, **extra),
        **template_kwargs,
    )
    if apply_lang_cookie and lang in LANGS:
        response = _with_lang_cookie(response, lang)
    if generated:
        response.set_cookie(
            CHAT_TOKEN_COOKIE,
            create_token(username),
            httponly=True,
            samesite="lax",
            path="/",
            max_age=CHAT_TOKEN_MAX_AGE,
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
        return _render(
            "index.html",
            request,
            "en",
            status_code=404,
            apply_lang_cookie=False,
            posts=get_posts(),
            error=_make_t("en")("language_not_found"),
            slug=None,
            language_switcher=_language_switcher(request, None, None),
        )
    posts = get_posts(lang)
    return _render(
        "index.html",
        request,
        lang,
        posts=posts,
        room="offtopic",
        slug=None,
        language_switcher=_language_switcher(request, lang, None),
    )


@router.get("/tags/{tag}")
def read_tag_redirect(request: Request, tag: str):
    return RedirectResponse(f"/{_preferred_lang(request)}/tags/{tag}")


@router.get("/{lang}/tags/{tag}")
def read_tag(request: Request, lang: str, tag: str):
    if lang not in LANGS:
        return RedirectResponse(f"/{_preferred_lang(request)}/tags/{tag}")
    posts = [p for p in get_posts(lang) if tag in (p.get("tags") or [])]
    return _render(
        "index.html",
        request,
        lang,
        posts=posts,
        tag=tag,
        room="offtopic",
        slug=None,
        language_switcher=_language_switcher(request, lang, None),
    )


@router.get("/{lang}/{slug:path}")
def read_item(request: Request, lang: str, slug: str):
    if lang not in LANGS:
        legacy = get_post(f"{lang}/{slug}")
        if legacy:
            legacy_lang = legacy.get("lang") or "en"
            return _render(
                "post.html",
                request,
                legacy_lang,
                post=legacy,
                room=legacy.get("slug"),
                slug=legacy.get("slug"),
                language_switcher=_language_switcher(request, legacy_lang, legacy.get("slug")),
            )
        return _render(
            "index.html",
            request,
            "en",
            status_code=404,
            apply_lang_cookie=False,
            posts=get_posts(),
            error=_make_t("en")("post_not_found"),
            slug=None,
            language_switcher=_language_switcher(request, None, None),
        )
    post = get_post(slug, lang)
    if not post:
        return _render(
            "index.html",
            request,
            lang,
            status_code=404,
            posts=get_posts(lang),
            error=_make_t(lang)("post_not_found"),
            slug=slug,
            language_switcher=_language_switcher(request, lang, slug),
        )
    return _render(
        "post.html",
        request,
        lang,
        post=post,
        room=slug,
        slug=slug,
        language_switcher=_language_switcher(request, lang, slug),
    )
