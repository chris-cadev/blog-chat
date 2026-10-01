import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        yield br
        br.close()


@pytest.fixture()
def page(browser):
    pg = browser.new_page()
    yield pg
    pg.close()


class TestI18nStrings:
    def test_index_strings_per_language(self, page, live_server):
        expected = {
            "en": {
                "title": "Blog Posts",
                "tagline": "Thoughts on software, life, and the things in between.",
                "privacy": "Privacy",
                "terms": "Terms",
            },
            "es": {
                "title": "Posts",
                "tagline": "Pensamientos sobre software, la vida y todo lo que hay en medio.",
                "privacy": "Privacidad",
                "terms": "Términos",
            },
            "fr": {
                "title": "Articles du blog",
                "tagline": "Pensées sur le logiciel, la vie et tout ce qu'il y a entre les deux.",
                "privacy": "Confidentialité",
                "terms": "Conditions",
            },
        }
        for lang, strings in expected.items():
            page.goto(f"{live_server}/{lang}/")
            assert page.locator("h1.page-title").inner_text() == strings["title"]
            assert page.locator(".page-subtitle").inner_text() == strings["tagline"]
            nav_text = page.locator(".footer-nav").inner_text()
            assert strings["privacy"] in nav_text
            assert strings["terms"] in nav_text

    def test_tags_page_strings_per_language(self, page, live_server):
        expected = {
            "en": ("Tags", "Browse posts by topic."),
            "es": ("Tags", "Explora las publicaciones por tema."),
            "fr": ("Étiquettes", "Parcourir les articles par thématique."),
        }
        for lang, (title, subtitle) in expected.items():
            page.goto(f"{live_server}/{lang}/tags")
            assert page.locator("h1.page-title").inner_text() == title
            assert page.locator("p.page-subtitle").inner_text() == subtitle

    def test_chat_panel_strings_per_language(self, page, live_server):
        expected = {
            "en": {"send": "Send", "placeholder": "Type a message…"},
            "es": {"send": "Enviar", "placeholder": "Escribe un mensaje…"},
            "fr": {"send": "Envoyer", "placeholder": "Écrivez un message…"},
        }
        for lang, strings in expected.items():
            page.goto(f"{live_server}/{lang}/")
            assert page.locator("#chat-send").inner_text() == strings["send"]
            assert page.locator("#chat-input").get_attribute("placeholder") == strings["placeholder"]
