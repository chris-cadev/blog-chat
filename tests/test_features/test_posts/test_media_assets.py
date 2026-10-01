import re
from pathlib import Path

import pytest

CONTENT = Path("content")
PUBLISHED_LANGS = ("en", "es", "fr", "mixed")

_MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
_HTML_SRC_RE = re.compile(r'(?:img|source|video|audio)\s[^>]*src="([^"]+)"')
_LEGACY = ("/static/posts/", "/drafts/")


def _slug(md: Path) -> str:
    m = re.search(r"^slug:\s*(.+)$", md.read_text(encoding="utf-8"), re.M)
    return m.group(1).strip().strip("\"'") if m else md.stem


def _published_posts():
    for lang in PUBLISHED_LANGS:
        d = CONTENT / lang
        if not d.is_dir():
            continue
        for md in sorted(d.glob("*.md")):
            yield lang, _slug(md), md


def _local_refs(md: Path):
    text = md.read_text(encoding="utf-8")
    refs = []
    for rx in (_MD_IMG_RE, _HTML_SRC_RE):
        for m in rx.finditer(text):
            ref = m.group(1).strip()
            if ref.startswith(("http://", "https://", "mailto:", "data:", "#")):
                continue
            refs.append(ref)
    return refs


def _ref_cases():
    cases = []
    for lang, slug, md in _published_posts():
        for ref in _local_refs(md):
            cases.append(pytest.param(md, ref, id=f"{lang}/{slug}::{ref}"))
    return cases


def _post_cases():
    return [
        pytest.param(lang, slug, md, id=f"{lang}/{slug}")
        for lang, slug, md in _published_posts()
    ]


@pytest.mark.parametrize("md,ref", _ref_cases())
def test_published_media_ref_exists(md, ref):
    """Every local media ref in a published post must live under content/assets/."""
    if ref.startswith(_LEGACY):
        pytest.fail(f"legacy absolute media path in {md}: {ref}")
    if ref.startswith("/"):
        return
    resolved = (md.parent / ref).resolve()
    assert resolved.is_file(), f"{md}: missing media {ref} -> {resolved}"
    assets = (CONTENT / "assets").resolve()
    try:
        resolved.relative_to(assets)
    except ValueError:
        pytest.fail(f"{md}: media not under content/assets: {ref} -> {resolved}")


@pytest.mark.parametrize("lang,slug,md", _post_cases())
def test_parsed_post_has_no_legacy_media_urls(lang, slug, md):
    """Rendered markdown must not point at /static/posts or /drafts for local media."""
    from blog_chat.features.posts.parser import parse_markdown_file

    content = parse_markdown_file(md)["content"]
    for legacy in _LEGACY:
        assert legacy not in content, f"{lang}/{slug}: still references {legacy}"
