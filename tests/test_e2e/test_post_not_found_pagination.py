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


class TestPostNotFoundPaginationE2E:
    """Missing-post pages share index pagination; only the banner differs."""

    def test_missing_post_shows_error_and_pagination(self, page, live_server):
        page.goto(f"{live_server}/en/does-not-exist")
        assert page.locator("[role=alert]").inner_text() == "Post not found"
        assert page.locator("nav.pagination").count() == 1

    def test_missing_post_page_2_matches_index(self, page, live_server):
        page.goto(f"{live_server}/en/?page=2")
        index_cards = page.locator(".post-card-link").all_inner_texts()

        page.goto(f"{live_server}/en/does-not-exist?page=2")
        assert page.locator("[role=alert]").inner_text() == "Post not found"
        not_found_cards = page.locator(".post-card-link").all_inner_texts()
        assert not_found_cards == index_cards

    def test_pagination_click_stays_on_missing_url(self, page, live_server):
        page.goto(f"{live_server}/en/does-not-exist")
        page.click(".pagination-link:text('2')")
        page.wait_for_url("**/en/does-not-exist?page=2", timeout=5000)
        assert page.locator("[role=alert]").inner_text() == "Post not found"
        assert "does-not-exist" in page.url

    def test_missing_post_same_page_count_as_index(self, page, live_server):
        page.goto(f"{live_server}/en/")
        index_last = page.locator(".pagination-last").get_attribute("href")
        index_page = int(index_last.rsplit("page=", 1)[-1])

        page.goto(f"{live_server}/en/does-not-exist")
        not_found_last = page.locator(".pagination-last").get_attribute("href")
        assert not_found_last == f"/en/does-not-exist?page={index_page}"

    def test_switch_lang_from_missing_post_preserves_page(self, page, live_server):
        page.goto(f"{live_server}/en/does-not-exist")
        page.click(".pagination-link:text('2')")
        page.wait_for_url("**/en/does-not-exist?page=2", timeout=5000)

        page.click("[data-track-language='es']")
        page.wait_for_url("**/es/?page=2", timeout=5000)
        assert page.locator("[role=alert]").count() == 0

    def test_direct_missing_post_page_lang_links_include_page(self, page, live_server):
        page.goto(f"{live_server}/en/does-not-exist?page=2")
        es_href = page.locator("[data-track-language='es']").get_attribute("href")
        assert es_href.endswith("/es/?page=2")
        fr_href = page.locator("[data-track-language='fr']").get_attribute("href")
        assert fr_href.endswith("/fr/?page=2")
