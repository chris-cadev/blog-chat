import re

from fastapi.testclient import TestClient

from blog_chat.app import app


class TestLangSwitcherPreservesPage:
    """Language switcher on paginated index pages should preserve ?page=N."""

    def _lang_links(self, html: str) -> dict[str, str]:
        """Extract lang-switcher hrefs from rendered HTML."""
        block = re.search(
            r'<div[^>]*class=lang-switcher[^>]*>(.*?)</div>', html, re.DOTALL
        )
        assert block, "lang-switcher div not found"
        links = {}
        for m in re.finditer(r'href="?([^"\s>]+)"?[^>]*lang=(\w+)', block.group(1)):
            href, lang = m.group(1), m.group(2)
            links[lang] = href
        return links

    def test_page1_no_page_param(self):
        with TestClient(app) as client:
            resp = client.get("/en/")
            assert resp.status_code == 200
            links = self._lang_links(resp.text)
            for lang in ("es", "fr"):
                assert lang in links
                assert "page=" not in links[lang]

    def test_page2_preserves_page(self):
        with TestClient(app) as client:
            resp = client.get("/en/?page=2")
            assert resp.status_code == 200
            links = self._lang_links(resp.text)
            for lang in ("es", "fr"):
                assert links[lang] == f"/{lang}/?page=2"

    def test_page3_preserves_page(self):
        with TestClient(app) as client:
            resp = client.get("/en/?page=3")
            assert resp.status_code == 200
            links = self._lang_links(resp.text)
            for lang in ("es", "fr"):
                assert links[lang] == f"/{lang}/?page=3"

    def test_switch_from_spanish_preserves_page(self):
        with TestClient(app) as client:
            resp = client.get("/es/?page=2")
            assert resp.status_code == 200
            links = self._lang_links(resp.text)
            for lang in ("en", "fr"):
                assert links[lang] == f"/{lang}/?page=2"

    def test_active_lang_links_to_self_without_page_on_page1(self):
        with TestClient(app) as client:
            resp = client.get("/en/")
            links = self._lang_links(resp.text)
            assert links["en"] == "/en/"

    def test_active_lang_links_to_self_with_page_on_page2(self):
        with TestClient(app) as client:
            resp = client.get("/en/?page=2")
            links = self._lang_links(resp.text)
            assert links["en"] == "/en/?page=2"
