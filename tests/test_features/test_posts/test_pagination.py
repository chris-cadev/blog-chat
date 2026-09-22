"""Tests for pagination display following HCI principles.

HCI guidelines tested:
- Current page is clearly indicated (aria-current, visual distinction)
- First and last page always visible (orientation landmarks)
- Windowed pages around current (±2 context)
- Ellipsis for gaps (reduces cognitive load)
- Prev/Next affordances with correct disabled states
- Accessible markup (aria-label, aria-current)
- HTMX partial rendering for SPA-like navigation
"""

import re

import pytest
from fastapi.testclient import TestClient

from blog_chat.app import app
from blog_chat.features.posts.routes import _paginate


# ── _paginate unit tests ──────────────────────────────────────


class TestPaginate:
    def test_empty_list(self):
        items, total, page = _paginate([], 1)
        assert items == []
        assert total == 1
        assert page == 1

    def test_single_page(self):
        items = list(range(5))
        result, total, page = _paginate(items, 1)
        assert result == [0, 1, 2, 3, 4]
        assert total == 1
        assert page == 1

    def test_exact_page_boundary(self):
        items = list(range(20))
        _, total, _ = _paginate(items, 1)
        assert total == 2

    def test_clamps_page_above(self):
        items = list(range(15))
        _, total, page = _paginate(items, 999)
        assert total == 2
        assert page == 2

    def test_clamps_page_below(self):
        items = list(range(15))
        _, total, page = _paginate(items, 0)
        assert total == 2
        assert page == 1

    def test_negative_page(self):
        items = list(range(15))
        _, _, page = _paginate(items, -5)
        assert page == 1

    def test_returns_correct_slice(self):
        items = list(range(25))
        page1, _, _ = _paginate(items, 1)
        page2, _, _ = _paginate(items, 2)
        page3, _, _ = _paginate(items, 3)
        assert page1 == list(range(10))
        assert page2 == list(range(10, 20))
        assert page3 == list(range(20, 25))

    def test_total_pages_calculation(self):
        assert _paginate(list(range(1)), 1)[1] == 1
        assert _paginate(list(range(10)), 1)[1] == 1
        assert _paginate(list(range(11)), 1)[1] == 2
        assert _paginate(list(range(20)), 1)[1] == 2
        assert _paginate(list(range(21)), 1)[1] == 3


# ── Helpers ───────────────────────────────────────────────────


def _make_posts(tmp_path, count):
    """Create *count* markdown posts in tmp_path for pagination testing."""
    for i in range(count):
        (tmp_path / f"post-{i:03d}.md").write_text(
            f"---\ntitle: Post {i}\nslug: post-{i:03d}\n"
            f"created: '2024-01-{i % 28 + 1:02d}'\nlang: en\n"
            f"tags: []\n---\n\nBody {i}",
            encoding="utf-8",
        )


def _pagination_html(html: str) -> str:
    """Extract the <nav class="pagination"> block from the page."""
    m = re.search(r'<nav[^>]*class="?pagination"?[^>]*>.*?</nav>', html, re.DOTALL)
    return m.group(0) if m else ""


def _page_numbers(html: str) -> list[int]:
    """Extract visible page numbers from pagination (links + current)."""
    nav = _pagination_html(html)
    nums = []
    for m in re.finditer(
        r'class="?pagination-(?:current|link)"?[^>]*>(\d+)<', nav
    ):
        nums.append(int(m.group(1)))
    return nums


def _has_ellipsis(html: str) -> bool:
    nav = _pagination_html(html)
    return "pagination-ellipsis" in nav


# ── Integration tests: HCI pagination display ─────────────────


@pytest.fixture
def many_posts(tmp_path, monkeypatch):
    _make_posts(tmp_path, 55)
    monkeypatch.setattr("blog_chat.features.posts.services.CONTENT_DIR", tmp_path)
    return tmp_path


class TestPaginationHCIDisplay:
    """Windowed pagination with ellipsis, first/last landmarks, prev/next."""

    def test_first_page_always_visible(self, many_posts):
        with TestClient(app) as client:
            resp = client.get("/en/")
            nums = _page_numbers(resp.text)
            assert 1 in nums

    def test_last_page_always_visible(self, many_posts):
        with TestClient(app) as client:
            resp = client.get("/en/")
            nums = _page_numbers(resp.text)
            assert 6 in nums

    def test_current_page_highlighted(self, many_posts):
        with TestClient(app) as client:
            resp = client.get("/en/?page=3")
            nav = _pagination_html(resp.text)
            assert re.search(r'aria-current=page class=pagination-current>3<', nav)

    def test_windowed_pages_around_current(self, many_posts):
        with TestClient(app) as client:
            resp = client.get("/en/?page=4")
            nums = _page_numbers(resp.text)
            assert 1 in nums
            assert 6 in nums
            for p in [2, 3, 4, 5, 6]:
                assert p in nums

    def test_ellipsis_on_first_page(self, many_posts):
        """Page 1 of 6: shows [1,2,3,...,6], skips 4,5."""
        with TestClient(app) as client:
            resp = client.get("/en/")
            assert _has_ellipsis(resp.text)
            nums = _page_numbers(resp.text)
            assert nums == [1, 2, 3, 6]

    def test_ellipsis_on_last_page(self, many_posts):
        """Page 6 of 6: shows [1,...,4,5,6], skips 2,3."""
        with TestClient(app) as client:
            resp = client.get("/en/?page=6")
            assert _has_ellipsis(resp.text)
            nums = _page_numbers(resp.text)
            assert nums == [1, 4, 5, 6]

    def test_no_ellipsis_on_middle_pages(self, many_posts):
        """Pages 3-4 of 6: window covers all, no ellipsis."""
        with TestClient(app) as client:
            for p in [3, 4]:
                resp = client.get(f"/en/?page={p}")
                assert not _has_ellipsis(resp.text), f"ellipsis on page {p}"
                nums = _page_numbers(resp.text)
                assert nums == [1, 2, 3, 4, 5, 6]

    def test_no_ellipsis_when_all_pages_fit(self, tmp_path, monkeypatch):
        """When total pages <= 3, window ±2 covers all from any page."""
        _make_posts(tmp_path, 30)  # 3 pages
        monkeypatch.setattr("blog_chat.features.posts.services.CONTENT_DIR", tmp_path)
        with TestClient(app) as client:
            for p in range(1, 4):
                resp = client.get(f"/en/?page={p}")
                assert not _has_ellipsis(resp.text), f"ellipsis on page {p}"

    def test_prev_disabled_on_first_page(self, many_posts):
        with TestClient(app) as client:
            resp = client.get("/en/")
            nav = _pagination_html(resp.text)
            assert "pagination-prev disabled" in nav

    def test_next_disabled_on_last_page(self, many_posts):
        with TestClient(app) as client:
            resp = client.get("/en/?page=6")
            nav = _pagination_html(resp.text)
            assert "pagination-next disabled" in nav

    def test_prev_enabled_on_middle_page(self, many_posts):
        with TestClient(app) as client:
            resp = client.get("/en/?page=3")
            nav = _pagination_html(resp.text)
            assert "pagination-prev" in nav
            assert "pagination-prev disabled" not in nav
            assert "page=2" in nav

    def test_next_enabled_on_middle_page(self, many_posts):
        with TestClient(app) as client:
            resp = client.get("/en/?page=3")
            nav = _pagination_html(resp.text)
            assert "pagination-next" in nav
            assert "pagination-next disabled" not in nav
            assert "page=4" in nav

    def test_nav_has_aria_label(self, many_posts):
        with TestClient(app) as client:
            resp = client.get("/en/")
            nav = _pagination_html(resp.text)
            assert 'aria-label="Page navigation"' in nav

    def test_current_page_has_aria_current(self, many_posts):
        with TestClient(app) as client:
            resp = client.get("/en/?page=2")
            nav = _pagination_html(resp.text)
            assert "aria-current=page" in nav

    def test_htmx_attributes_on_page_links(self, many_posts):
        with TestClient(app) as client:
            resp = client.get("/en/")
            nav = _pagination_html(resp.text)
            assert "hx-get=" in nav
            assert "hx-target=" in nav
            assert "hx-swap=" in nav
            assert "hx-push-url=" in nav

    def test_htmx_partial_render(self, many_posts):
        with TestClient(app) as client:
            resp = client.get(
                "/en/?page=2",
                headers={"HX-Request": "true"},
            )
            assert resp.status_code == 200
            assert "pagination" in resp.text
            assert "<html" not in resp.text


class TestPaginationSmallDataset:
    """Edge cases with few pages."""

    @pytest.fixture
    def few_posts(self, tmp_path, monkeypatch):
        _make_posts(tmp_path, 3)
        monkeypatch.setattr("blog_chat.features.posts.services.CONTENT_DIR", tmp_path)
        return tmp_path

    def test_no_pagination_widget_when_single_page(self, few_posts):
        with TestClient(app) as client:
            resp = client.get("/en/")
            assert "pagination" not in resp.text

    @pytest.fixture
    def two_pages(self, tmp_path, monkeypatch):
        _make_posts(tmp_path, 15)
        monkeypatch.setattr("blog_chat.features.posts.services.CONTENT_DIR", tmp_path)
        return tmp_path

    def test_two_pages_no_ellipsis(self, two_pages):
        with TestClient(app) as client:
            resp = client.get("/en/")
            nav = _pagination_html(resp.text)
            assert "pagination-ellipsis" not in nav
            nums = _page_numbers(resp.text)
            assert nums == [1, 2]

    def test_two_pages_prev_disabled_on_1(self, two_pages):
        with TestClient(app) as client:
            resp = client.get("/en/")
            nav = _pagination_html(resp.text)
            assert "pagination-prev disabled" in nav

    def test_two_pages_next_disabled_on_2(self, two_pages):
        with TestClient(app) as client:
            resp = client.get("/en/?page=2")
            nav = _pagination_html(resp.text)
            assert "pagination-next disabled" in nav
