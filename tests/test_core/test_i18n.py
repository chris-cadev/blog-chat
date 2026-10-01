from fastapi.testclient import TestClient
from starlette.requests import Request

from blog_chat.app import app
from blog_chat.core.i18n import (
    LANGS,
    TRANSLATIONS,
    make_t,
    preferred_lang,
)


def _request(
    *,
    cookie: str | None = None,
    accept_language: str | None = None,
) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if accept_language is not None:
        headers.append(
            (b"accept-language", accept_language.encode("ascii", "replace"))
        )
    if cookie is not None:
        headers.append((b"cookie", f"lang={cookie}".encode("ascii")))
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": headers,
        "client": ("testclient", 123),
        "server": ("testserver", 80),
    }
    return Request(scope)


def test_all_langs_have_same_keys():
    key_sets = {lang: set(TRANSLATIONS[lang]) for lang in LANGS}
    assert key_sets["en"] == key_sets["es"] == key_sets["fr"]


def test_no_empty_translations():
    for lang in LANGS:
        for key, value in TRANSLATIONS[lang].items():
            assert value, f"{lang}.{key} is empty"


def test_make_t_returns_translation():
    t = make_t("es")
    assert t("privacy") == "Privacidad"
    assert t("terms") == "Términos"


def test_make_t_falls_back_to_english():
    t = make_t(None)
    assert t("posts_title") == "Blog Posts"


def test_make_t_unknown_key_returns_key():
    t = make_t("fr")
    assert t("does_not_exist") == "does_not_exist"


class TestPreferredLang:
    """Cookie wins; else Accept-Language negotiation; else English."""

    def test_cookie_valid_lang_is_returned(self):
        for lang in LANGS:
            req = _request(cookie=lang)
            assert preferred_lang(req) == lang

    def test_cookie_overrides_accept_language(self):
        req = _request(cookie="fr", accept_language="es-MX,es;q=0.9,en;q=0.8")
        assert preferred_lang(req) == "fr"

    def test_invalid_cookie_falls_through_to_accept_language(self):
        req = _request(cookie="de", accept_language="es")
        assert preferred_lang(req) == "es"

    def test_accept_language_simple_code(self):
        req = _request(accept_language="es")
        assert preferred_lang(req) == "es"

    def test_accept_language_region_stripped_to_base(self):
        req = _request(accept_language="fr-CA")
        assert preferred_lang(req) == "fr"

    def test_accept_language_prefers_first_supported(self):
        req = _request(accept_language="en-US,en;q=0.9,es;q=0.8")
        assert preferred_lang(req) == "en"

    def test_accept_language_skips_unsupported_codes(self):
        req = _request(accept_language="de,ja,es;q=0.5")
        assert preferred_lang(req) == "es"

    def test_accept_language_highest_q_wins(self):
        req = _request(accept_language="fr;q=0.9,es;q=0.8")
        assert preferred_lang(req) == "fr"

    def test_accept_language_q_order_overrides_header_order(self):
        req = _request(accept_language="es;q=0.4,fr;q=0.9")
        assert preferred_lang(req) == "fr"

    def test_accept_language_equal_q_keeps_header_order(self):
        req = _request(accept_language="es;q=0.5,fr;q=0.5")
        assert preferred_lang(req) == "es"

    def test_accept_language_code_case_insensitive(self):
        req = _request(accept_language="ES")
        assert preferred_lang(req) == "es"

    def test_accept_language_whitespace_around_code(self):
        req = _request(accept_language=" en-US ")
        assert preferred_lang(req) == "en"

    def test_accept_language_malformed_q_treated_as_zero(self):
        req = _request(accept_language="es;q=abc,en;q=0.1")
        assert preferred_lang(req) == "en"

    def test_no_supported_language_falls_back_to_english(self):
        req = _request(accept_language="de,ja,ko")
        assert preferred_lang(req) == "en"

    def test_empty_accept_language_falls_back_to_english(self):
        req = _request(accept_language="")
        assert preferred_lang(req) == "en"

    def test_missing_accept_language_falls_back_to_english(self):
        req = _request()
        assert preferred_lang(req) == "en"


class TestPreferredLangCallSites:
    """Consumers in features/posts/routes.py resolve lang via preferred_lang."""

    def test_root_redirects_using_accept_language(self):
        with TestClient(app) as client:
            resp = client.get(
                "/",
                headers={"accept-language": "es-MX,es;q=0.9,en;q=0.8"},
                follow_redirects=False,
            )
        assert resp.status_code == 302
        assert resp.headers["location"] == "/es/"

    def test_root_redirects_using_cookie_over_accept_language(self):
        with TestClient(app) as client:
            client.cookies.set("lang", "fr")
            resp = client.get(
                "/",
                headers={"accept-language": "es"},
                follow_redirects=False,
            )
        assert resp.status_code == 302
        assert resp.headers["location"] == "/fr/"

    def test_root_redirects_to_english_when_no_signal(self):
        with TestClient(app) as client:
            resp = client.get("/", follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"] == "/en/"

    def test_tag_redirect_uses_cookie_lang(self):
        with TestClient(app) as client:
            client.cookies.set("lang", "fr")
            resp = client.get(
                "/tags/python",
                headers={"accept-language": "es"},
                follow_redirects=False,
            )
        assert resp.status_code == 307
        assert resp.headers["location"] == "/fr/tags/python"

    def test_invalid_lang_tag_redirect_uses_accept_language(self):
        with TestClient(app) as client:
            resp = client.get(
                "/de/tags/python",
                headers={"accept-language": "es"},
                follow_redirects=False,
            )
        assert resp.status_code == 307
        assert resp.headers["location"] == "/es/tags/python"

    def test_unknown_route_renders_404_in_preferred_lang(self):
        with TestClient(app) as client:
            resp = client.get(
                "/static/missing.css",
                headers={"accept-language": "fr-CA"},
            )
        assert resp.status_code == 404
        assert "Page introuvable" in resp.text

    def test_unknown_route_404_uses_cookie_lang(self):
        with TestClient(app) as client:
            client.cookies.set("lang", "fr")
            resp = client.get(
                "/static/missing.css",
                headers={"accept-language": "es"},
            )
        assert resp.status_code == 404
        assert "Page introuvable" in resp.text
        assert "Página no encontrada" not in resp.text
        assert "Page not found" not in resp.text
