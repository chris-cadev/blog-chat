import importlib.util
from datetime import datetime
from pathlib import Path

import pytest

script_dir = Path(__file__).resolve().parent.parent / "scripts"


def _load(name: str):
    path = script_dir / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


new_post = _load("new_post")
set_slug = _load("set_slug")


def test_create_draft(tmp_path, monkeypatch):
    monkeypatch.setattr(new_post, "DRAFTS_DIR", tmp_path / "content" / "_drafts")
    path = new_post.create_draft(title="Mi primer post", now=datetime(2026, 8, 28, 14, 30))
    assert path.name == "2026-08-28-1430.md"
    text = path.read_text()
    assert "title: Mi primer post" in text
    assert "created: '2026-08-28'" in text
    second = new_post.create_draft(now=datetime(2026, 8, 28, 14, 30))
    assert second.name == "2026-08-28-1430-2.md"


def test_assign_slug_moves_and_is_idempotent(tmp_path):
    content = tmp_path / "content"
    draft = new_post.create_draft(
        title="Hola", now=datetime(2026, 8, 28, 14, 30), drafts_dir=content / "_drafts"
    )
    target = set_slug.assign_slug(draft, "hola-mundo", "es", content)
    assert target == content / "es" / "hola-mundo.md"
    assert not draft.exists()
    text = target.read_text()
    assert "slug: hola-mundo" in text
    assert "lang: es" in text
    assert "lang_group: hola-mundo" in text
    assert "title: Hola" in text
    again = set_slug.assign_slug(target, "hola-mundo", "es", content)
    assert again == target


def test_assign_slug_conflict(tmp_path):
    content = tmp_path / "content"
    (content / "es").mkdir(parents=True)
    (content / "es" / "taken.md").write_text("---\nslug: taken\n---\n\n")
    draft = new_post.create_draft(now=datetime(2026, 8, 28, 14, 30), drafts_dir=content / "_drafts")
    with pytest.raises(ValueError):
        set_slug.assign_slug(draft, "taken", "es", content)


def test_assign_slug_refuses_overwrite(tmp_path):
    content = tmp_path / "content"
    draft = new_post.create_draft(now=datetime(2026, 8, 28, 14, 30), drafts_dir=content / "_drafts")
    draft.write_text("---\nslug: other\n---\n\n")
    with pytest.raises(ValueError):
        set_slug.assign_slug(draft, "new-slug", "es", content)