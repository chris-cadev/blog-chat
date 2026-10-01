import importlib.util
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from blog_chat.app import app
from blog_chat.features.posts.schema import article_schema, build_llms_txt, person_schema, website_schema


def _load_geo_qa():
    path = Path(__file__).resolve().parents[3] / "scripts" / "geo_qa.py"
    spec = importlib.util.spec_from_file_location("geo_qa", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


geo_qa = _load_geo_qa()


class TestSchemaBuilders:
    def test_article_schema_core_fields(self):
        data = article_schema(
            {"title": "Hola", "slug": "hola", "lang": "es", "created": "2026-01-01", "updated": "2026-01-02", "description": "Desc"}
        )
        assert data["@type"] == "Article"
        assert data["headline"] == "Hola"
        assert data["inLanguage"] == "es"
        assert data["mainEntityOfPage"].endswith("/es/hola")
        assert data["datePublished"] == "2026-01-01"
        assert data["dateModified"] == "2026-01-02"
        assert data["author"]["name"] == "Chris Camacho"

    def test_website_schema_has_publisher(self):
        data = website_schema()
        assert data["@type"] == "WebSite"
        assert data["publisher"]["@type"] == "Organization"

    def test_person_schema_same_as(self):
        data = person_schema("en")
        assert data["@type"] == "Person"
        assert any("github.com" in u for u in data["sameAs"])

    def test_build_llms_txt_groups_by_lang(self):
        text = build_llms_txt(
            [
                {"title": "A", "slug": "a", "lang": "en", "description": "About A"},
                {"title": "B", "slug": "b", "lang": "es", "description": "Sobre B"},
            ]
        )
        assert text.startswith("# Chrislabs Blog")
        assert "## English" in text
        assert "## Español" in text
        assert "[A](https://blog.chrislabs.net/en/a)" in text
        assert "[B](https://blog.chrislabs.net/es/b)" in text


class TestGeoEndpoints:
    def test_llms_txt_lists_posts(self, live_server):
        with TestClient(app) as client:
            resp = client.get("/llms.txt")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/plain")
        assert resp.text.startswith("# Chrislabs Blog")
        assert "/en/" in resp.text or "/es/" in resp.text

    def test_robots_mentions_sitemap_and_site_still_works(self, live_server):
        with TestClient(app) as client:
            robots = client.get("/robots.txt")
            sitemap = client.get("/sitemap.xml")
        assert robots.status_code == 200
        assert "Sitemap:" in robots.text
        assert sitemap.status_code == 200
        assert "urlset" in sitemap.text

    def test_about_page_renders_with_person_schema(self, live_server):
        with TestClient(app) as client:
            resp = client.get("/en/about")
        assert resp.status_code == 200
        assert "application/ld+json" in resp.text
        assert "Chris Camacho" in resp.text
        assert "schema.org" in resp.text

    def test_about_redirect_for_unknown_lang(self, live_server):
        with TestClient(app) as client:
            resp = client.get("/xx/about", follow_redirects=False)
        assert resp.status_code in (302, 307)
        assert "/about" in resp.headers["location"]

    def test_post_page_includes_article_jsonld(self, live_server):
        with TestClient(app) as client:
            resp = client.get("/en/first-post")
        assert resp.status_code == 200
        assert "application/ld+json" in resp.text
        assert '"@type": "Article"' in resp.text
        assert "schema.org" in resp.text

    def test_base_includes_website_jsonld(self, live_server):
        with TestClient(app) as client:
            resp = client.get("/en/")
        assert resp.status_code == 200
        assert "WebSite" in resp.text
        assert "application/ld+json" in resp.text

    def test_footer_links_about(self, live_server):
        with TestClient(app) as client:
            resp = client.get("/en/")
        assert "/en/about" in resp.text


class TestGeoQaScript:
    def test_analyze_flags_missing_description_and_alt(self, tmp_path):
        path = tmp_path / "bad.md"
        path.write_text(
            "---\ntitle: Bad\nslug: bad\ncreated: '2026-01-01'\n---\n\n"
            "Hello world with no description.\n\n![](/media/x.png)\n",
            encoding="utf-8",
        )
        post = geo_qa.parse_markdown_file(path)
        findings = geo_qa.analyze_post(post, path.read_text())
        codes = {c for _, c, _ in findings}
        assert "missing_description" in codes
        assert "missing_alt" in codes
        assert "no_external_links" in codes

    def test_analyze_ok_when_signals_present(self, tmp_path):
        body = (
            "Open with a concrete claim: latency dropped 40% after the fix.\n\n"
            "## Why did latency drop?\n\n"
            "We measured 120ms p95 before and 72ms after. "
            "See [the WCAG note](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) "
            "for contrast rules.\n\n"
            "![Latency chart showing 40 percent drop](/media/chart.png)\n"
        )
        path = tmp_path / "good.md"
        path.write_text(
            "---\ntitle: Good\nslug: good\ndescription: Latency dropped 40 percent after the fix.\n"
            "created: '2026-01-01'\nlang: en\n---\n\n" + body,
            encoding="utf-8",
        )
        post = geo_qa.parse_markdown_file(path)
        findings = geo_qa.analyze_post(post, path.read_text())
        errors = [c for level, c, _ in findings if level == "error"]
        assert errors == []
        codes = {c for _, c, _ in findings}
        assert "no_external_links" not in codes
        assert "no_statistics" not in codes
        assert "missing_alt" not in codes

    def test_cli_strict_exit_code(self, tmp_path, capsys):
        path = tmp_path / "draft.md"
        path.write_text("---\ntitle: T\nslug: t\n---\n\nBody only\n", encoding="utf-8")
        assert geo_qa.main([str(path), "--strict"]) == 1
        out = capsys.readouterr().out
        assert "missing_description" in out

    def test_cli_default_exit_zero(self, tmp_path):
        path = tmp_path / "draft.md"
        path.write_text("---\ntitle: T\nslug: t\n---\n\nBody only\n", encoding="utf-8")
        assert geo_qa.main([str(path)]) == 0
