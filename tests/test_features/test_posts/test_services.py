import tempfile
from pathlib import Path

import pytest

from blog_chat.features.posts.services import get_post, get_posts


@pytest.fixture
def content_dir(tmp_path, monkeypatch):
    for lang in ("en", "es", "fr"):
        (tmp_path / lang).mkdir()
        (tmp_path / lang / f"post-{lang}.md").write_text(
            f"---\ntitle: Post {lang}\nslug: post\ntags: []\ncreated: '2024-01-01'\nlang: {lang}\nlang_group: post\n---\n\nBody {lang}",
            encoding="utf-8",
        )
    monkeypatch.setattr("blog_chat.features.posts.services.CONTENT_DIR", tmp_path)
    return tmp_path


class TestGetPostsByLanguage:
    def test_get_posts_all_languages(self, content_dir):
        posts = get_posts()
        assert len(posts) == 3

    def test_get_posts_filtered_by_lang(self, content_dir):
        en_posts = get_posts("en")
        assert len(en_posts) == 1
        assert en_posts[0]["lang"] == "en"
        assert en_posts[0]["slug"] == "post"

    def test_get_posts_unknown_lang_returns_empty(self, content_dir):
        assert get_posts("xx") == []

    def test_get_post_matches_lang(self, content_dir):
        post = get_post("post", "es")
        assert post is not None
        assert post["lang"] == "es"
        assert post["content"] == "Body es"

    def test_get_post_wrong_lang_returns_none(self, content_dir):
        assert get_post("post", "fr") is not None  # exists

    def test_get_post_missing_slug_returns_none(self, content_dir):
        assert get_post("nope", "en") is None


class TestGetPostsOrdering:
    @pytest.fixture
    def ordering_dir(self, tmp_path, monkeypatch):
        posts = {
            "b.md": "---\ntitle: B\nslug: b\ncreated: '2024-01-01'\nlang: en\n---\n\nB",
            "a.md": "---\ntitle: A\nslug: a\ncreated: '2024-01-01'\nlang: en\n---\n\nA",
            "z.md": "---\ntitle: Z\nslug: z\ncreated: '2023-01-01'\nlang: en\n---\n\nZ",
            "nodate.md": "---\ntitle: N\nslug: nodate\nlang: en\n---\n\nN",
            "adate.md": "---\ntitle: AD\nslug: adate\nlang: en\n---\n\nAD",
        }
        for name, body in posts.items():
            (tmp_path / name).write_text(body, encoding="utf-8")
        monkeypatch.setattr("blog_chat.features.posts.services.CONTENT_DIR", tmp_path)
        return tmp_path

    def test_newest_first_same_date_reverse_alpha(self, ordering_dir):
        slugs = [p["slug"] for p in get_posts("en")]
        assert slugs == ["b", "a", "z", "nodate", "adate"]


class TestGetPostExactLangBeatsLangless:
    def test_exact_lang_wins_over_langless_shadow(self, tmp_path, monkeypatch):
        # regression: a lang-less (or broken-YAML) post must not shadow
        # the real translation, regardless of walk order
        (tmp_path / "a_langless.md").write_text(
            "---\ntitle: Ghost\nslug: post\ntags: []\ncreated: '2024-01-01'\n---\n\nGhost body",
            encoding="utf-8",
        )
        (tmp_path / "z_translation.md").write_text(
            "---\ntitle: Real\nslug: post\ntags: []\ncreated: '2024-01-01'\nlang: es\nlang_group: post\n---\n\nCuerpo real",
            encoding="utf-8",
        )
        monkeypatch.setattr("blog_chat.features.posts.services.CONTENT_DIR", tmp_path)
        post = get_post("post", "es")
        assert post is not None
        assert post["lang"] == "es"
        assert post["content"] == "Cuerpo real"

    def test_langless_still_serves_as_fallback(self, tmp_path, monkeypatch):
        (tmp_path / "seed.md").write_text(
            "---\ntitle: Seed\nslug: post\ntags: []\ncreated: '2024-01-01'\n---\n\nBody",
            encoding="utf-8",
        )
        monkeypatch.setattr("blog_chat.features.posts.services.CONTENT_DIR", tmp_path)
        post = get_post("post", "es")
        assert post is not None
        assert post["content"] == "Body"


class TestGetPostLanguageNeutralFallback:
    def test_langless_post_matches_any_lang(self, tmp_path, monkeypatch):
        (tmp_path / "seed.md").write_text(
            "---\ntitle: Seed\nslug: platform/first\ntags: []\ncreated: '2024-01-01'\n---\n\nBody",
            encoding="utf-8",
        )
        monkeypatch.setattr("blog_chat.features.posts.services.CONTENT_DIR", tmp_path)
        post = get_post("platform/first", "en")
        assert post is not None
        assert post["slug"] == "platform/first"


class TestLegalPagesExcluded:
    @pytest.fixture
    def legal_dir(self, tmp_path, monkeypatch):
        (tmp_path / "en").mkdir()
        (tmp_path / "es").mkdir()
        (tmp_path / "legal").mkdir()
        (tmp_path / "legal" / "en").mkdir()
        (tmp_path / "legal" / "es").mkdir()
        (tmp_path / "en" / "blog-post.md").write_text(
            "---\ntitle: Blog Post\nslug: blog-post\ncreated: '2024-01-01'\nlang: en\n---\n\nBody",
            encoding="utf-8",
        )
        (tmp_path / "legal" / "en" / "privacy-policy.md").write_text(
            "---\ntitle: Privacy Policy\nslug: privacy-policy\ncreated: '2024-01-01'\nlang: en\n---\n\nLegal body",
            encoding="utf-8",
        )
        (tmp_path / "legal" / "en" / "terms.md").write_text(
            "---\ntitle: Terms\nslug: terms\ncreated: '2024-01-01'\nlang: en\n---\n\nLegal body",
            encoding="utf-8",
        )
        monkeypatch.setattr("blog_chat.features.posts.services.CONTENT_DIR", tmp_path)
        return tmp_path

    def test_get_posts_excludes_legal_pages(self, legal_dir):
        posts = get_posts("en")
        slugs = [p["slug"] for p in posts]
        assert "blog-post" in slugs
        assert "privacy-policy" not in slugs
        assert "terms" not in slugs
        assert len(posts) == 1

    def test_get_post_can_fetch_legal_pages(self, legal_dir):
        privacy = get_post("privacy-policy", "en")
        assert privacy is not None
        assert privacy["title"] == "Privacy Policy"
        terms = get_post("terms", "en")
        assert terms is not None
        assert terms["title"] == "Terms"
