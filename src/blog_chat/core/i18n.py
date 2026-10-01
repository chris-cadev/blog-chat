from fastapi import Request
from fastapi.responses import Response

LANGS = ("en", "es", "fr")
LANG_FLAGS = {"en": "🇺🇸", "es": "🇲🇽", "fr": "🇫🇷"}
LANG_NAMES = {"en": "English", "es": "Español", "fr": "Français"}
LANG_COOKIE = "lang"
LANG_COOKIE_MAX_AGE = 60 * 60 * 24 * 365

TRANSLATIONS = {
    "en": {
        "home": "Home",
        "tagline": "Thoughts on software, life, and the things in between.",
        "back_to_posts": "Back to all posts",
        "posts_title": "Blog Posts",
        "privacy": "Privacy",
        "terms": "Terms",
        "no_posts": "No posts found.",
        "posts_tagged": "Posts tagged",
        "tags": "Tags",
        "all_posts": "All posts",
        "tags_subtitle": "Browse posts by topic.",
        "tag_not_found": "Tag not found",
        "chat_title": "Off-topic",
        "enter_name": "Enter your name",
        "join": "Join",
        "logged_in_as": "Logged in as",
        "change_username": "Change username",
        "type_message": "Type a message…",
        "enter_to_send": "Press Enter to send",
        "send": "Send",
        "save": "Save",
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
        "page_not_found": "Page not found",
        "people_online": "People currently in chat",
        "online": "online",
    },
    "es": {
        "home": "Inicio",
        "tagline": "Pensamientos sobre software, la vida y todo lo que hay en medio.",
        "back_to_posts": "Volver a todos los artículos",
        "posts_title": "Posts",
        "privacy": "Privacidad",
        "terms": "Términos",
        "no_posts": "No se encontraron artículos.",
        "posts_tagged": "Posts etiquetados",
        "tags": "Tags",
        "all_posts": "Todos los artículos",
        "tags_subtitle": "Explora las publicaciones por tema.",
        "tag_not_found": "Tag no encontrado",
        "chat_title": "Fuera de tema",
        "enter_name": "Escribe tu nombre",
        "join": "Unirse",
        "logged_in_as": "Conectado como",
        "change_username": "Cambiar nombre",
        "type_message": "Escribe un mensaje…",
        "enter_to_send": "Enter para enviar",
        "send": "Enviar",
        "save": "Guardar",
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
        "page_not_found": "Página no encontrada",
        "people_online": "Personas en el chat ahora",
        "online": "en línea",
    },
    "fr": {
        "home": "Accueil",
        "tagline": "Pensées sur le logiciel, la vie et tout ce qu'il y a entre les deux.",
        "back_to_posts": "Retour à tous les articles",
        "posts_title": "Articles du blog",
        "privacy": "Confidentialité",
        "terms": "Conditions",
        "no_posts": "Aucun article trouvé.",
        "posts_tagged": "Articles tagués",
        "tags": "Étiquettes",
        "all_posts": "Tous les articles",
        "tags_subtitle": "Parcourir les articles par thématique.",
        "tag_not_found": "Tag non trouvé",
        "chat_title": "Hors sujet",
        "enter_name": "Saisissez votre nom",
        "join": "Rejoindre",
        "logged_in_as": "Connecté en tant que",
        "change_username": "Changer de nom",
        "type_message": "Écrivez un message…",
        "enter_to_send": "Entrée pour envoyer",
        "send": "Envoyer",
        "save": "Enregistrer",
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
        "page_not_found": "Page introuvable",
        "people_online": "Personnes actuellement dans le chat",
        "online": "en ligne",
    },
}


def make_t(lang: str | None):
    table = TRANSLATIONS.get(lang or "en", TRANSLATIONS["en"])

    def translate(key: str) -> str:
        return table.get(key, key)

    return translate


def language_switcher(request: Request, lang: str | None, slug: str | None) -> list[dict]:
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


def preferred_lang(request: Request) -> str:
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


def with_lang_cookie(response: Response, lang: str) -> Response:
    response.set_cookie(
        LANG_COOKIE,
        lang,
        max_age=LANG_COOKIE_MAX_AGE,
        path="/",
        samesite="lax",
        httponly=True,
    )
    return response
