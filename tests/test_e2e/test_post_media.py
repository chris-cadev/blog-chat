import re
from pathlib import Path

import pytest
import requests

CONTENT = Path("content")
PUBLISHED_LANGS = ("en", "es", "fr", "mixed")
_MEDIA_URL_RE = re.compile(r'(?:src|href)=["\']?(/media/[^"\'\s>]+)')


def _slug(md: Path) -> str:
    m = re.search(r"^slug:\s*(.+)$", md.read_text(encoding="utf-8"), re.M)
    return m.group(1).strip().strip("\"'") if m else md.stem


def _published_posts():
    for lang in PUBLISHED_LANGS:
        d = CONTENT / lang
        if not d.is_dir():
            continue
        for md in sorted(d.glob("*.md")):
            yield lang, _slug(md)


@pytest.mark.parametrize(
    "lang,slug",
    [pytest.param(lang, slug, id=f"{lang}/{slug}") for lang, slug in _published_posts()],
)
def test_post_page_media_urls_return_200(lang, slug, live_server):
    """Every /media/ URL on a published post page must be served (no 404s)."""
    page = requests.get(f"{live_server}/{lang}/{slug}", timeout=30)
    assert page.status_code == 200, f"{lang}/{slug}: page HTTP {page.status_code}"

    media_urls = sorted(set(_MEDIA_URL_RE.findall(page.text)))
    for url in media_urls:
        resp = requests.get(f"{live_server}{url}", timeout=60, stream=True)
        resp.close()
        assert resp.status_code == 200, f"{lang}/{slug}: {url} -> HTTP {resp.status_code}"


@pytest.mark.parametrize(
    "lang,slug",
    [pytest.param(lang, slug, id=f"{lang}/{slug}") for lang, slug in _published_posts()],
)
def test_post_page_has_no_legacy_static_posts_refs(lang, slug, live_server):
    page = requests.get(f"{live_server}/{lang}/{slug}", timeout=30)
    assert page.status_code == 200
    assert "/static/posts/" not in page.text, f"{lang}/{slug}: HTML still uses /static/posts/"
