import re

from fastapi.testclient import TestClient

from blog_chat.app import app


def _html_attr(text: str, name: str) -> str | None:
    m = re.search(rf'<html[^>]*\s{name}="?([^"\s>]+)"?', text)
    return m.group(1) if m else None


class TestThemeSSR:
    def test_light_cookie_renders_light_theme_on_html(self):
        with TestClient(app) as client:
            client.cookies.set("theme-mode", "nord-light")
            response = client.get("/en/")
            assert response.status_code == 200
            assert _html_attr(response.text, "data-theme-mode") == "light"
            assert _html_attr(response.text, "data-theme") == "nord-light"

    def test_dark_cookie_renders_dark_theme_on_html(self):
        with TestClient(app) as client:
            client.cookies.set("theme-mode", "nord")
            response = client.get("/en/")
            assert response.status_code == 200
            assert _html_attr(response.text, "data-theme-mode") == "dark"
            assert _html_attr(response.text, "data-theme") == "nord"

    def test_legacy_dark_light_cookie_values(self):
        with TestClient(app) as client:
            client.cookies.set("theme-mode", "light")
            response = client.get("/en/")
            assert _html_attr(response.text, "data-theme-mode") == "light"

            client.cookies.set("theme-mode", "dark")
            response = client.get("/en/")
            assert _html_attr(response.text, "data-theme-mode") == "dark"

    def test_missing_cookie_defaults_to_dark(self):
        with TestClient(app) as client:
            response = client.get("/en/")
            assert response.status_code == 200
            assert _html_attr(response.text, "data-theme-mode") == "dark"

    def test_inline_theme_script_has_csp_nonce(self):
        with TestClient(app) as client:
            response = client.get("/en/")
            csp = response.headers.get("content-security-policy", "")
            csp_nonce = re.search(r"nonce-([A-Za-z0-9_-]+)", csp)
            assert csp_nonce, "expected nonce in CSP"
            script = re.search(r"<script([^>]*)>", response.text)
            assert script, "expected a script tag"
            nonce_attr = re.search(
                r'nonce="?([A-Za-z0-9_-]+)"?', script.group(1)
            )
            assert nonce_attr, "expected a nonce on the inline script"
            assert nonce_attr.group(1) == csp_nonce.group(1)
