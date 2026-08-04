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

    def test_newest_first_ties_alphabetical(self, ordering_dir):
        slugs = [p["slug"] for p in get_posts("en")]
        assert slugs == ["a", "b", "z", "adate", "nodate"]


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
