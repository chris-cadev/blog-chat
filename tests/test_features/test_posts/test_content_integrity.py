import re
from pathlib import Path

import pytest
import yaml

from blog_chat.features.posts.parser import parse_markdown_file

ROOT = Path(__file__).resolve().parents[3]
CONTENT_DIR = ROOT / "content"
LANGS = ("en", "es", "fr")
REQUIRED_KEYS = ("title", "slug", "lang", "lang_group")
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _lang_files() -> list[Path]:
    files = []
    for lang in LANGS:
        d = CONTENT_DIR / lang
        if d.is_dir():
            files.extend(sorted(d.glob("*.md")))
    return files


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.match(text)
    assert m, f"{path}: missing frontmatter"
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        pytest.fail(f"{path}: invalid YAML ({e})")
    assert isinstance(data, dict), f"{path}: frontmatter is not a mapping"
    return data


class TestContentFrontmatter:
    @pytest.mark.parametrize("path", _lang_files(), ids=lambda p: f"{p.parent.name}/{p.name}")
    def test_valid_yaml(self, path):
        _frontmatter(path)  # fails on YAMLError (e.g. unquoted `:` in title/description)

    @pytest.mark.parametrize("path", _lang_files(), ids=lambda p: f"{p.parent.name}/{p.name}")
    def test_required_keys_and_lang(self, path):
        fm = _frontmatter(path)
        for key in REQUIRED_KEYS:
            assert fm.get(key), f"{path}: missing {key}"
        assert fm["lang"] == path.parent.name, f"{path}: lang={fm['lang']} not in {path.parent.name}/"

    @pytest.mark.parametrize("path", _lang_files(), ids=lambda p: f"{p.parent.name}/{p.name}")
    def test_parsed_title_not_slug_fallback(self, path):
        post = parse_markdown_file(path)
        assert post["title"] != path.stem, f"{path}: title fell back to slug (broken frontmatter?)"

    def test_no_duplicate_slug_per_lang(self):
        seen: dict[tuple, Path] = {}
        for path in _lang_files():
            fm = _frontmatter(path)
            key = (fm["slug"], fm["lang"])
            assert key not in seen, f"duplicate slug+lang {key}: {seen[key]} and {path}"
            seen[key] = path
