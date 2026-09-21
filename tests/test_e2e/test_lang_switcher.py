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


class TestLangSwitcherPagination:
    def test_page2_switch_lang_preserves_page(self, page, live_server):
        page.goto(f"{live_server}/en/")
        page.click(".pagination-link:text('2')")
        page.wait_for_url("**/en/?page=2", timeout=5000)

        page.click("[data-track-language='es']")
        page.wait_for_url("**/es/?page=2", timeout=5000)

    def test_page3_switch_lang_preserves_page(self, page, live_server):
        page.goto(f"{live_server}/en/")
        page.click(".pagination-link:text('3')")
        page.wait_for_url("**/en/?page=3", timeout=5000)

        page.click("[data-track-language='es']")
        page.wait_for_url("**/es/?page=3", timeout=5000)

    def test_switch_back_preserves_page(self, page, live_server):
        page.goto(f"{live_server}/en/")
        page.click(".pagination-link:text('2')")
        page.wait_for_url("**/en/?page=2", timeout=5000)

        page.click("[data-track-language='es']")
        page.wait_for_url("**/es/?page=2", timeout=5000)

        page.click("[data-track-language='en']")
        page.wait_for_url("**/en/?page=2", timeout=5000)

    def test_page1_no_page_param(self, page, live_server):
        page.goto(f"{live_server}/en/")
        es_link = page.locator("[data-track-language='es']")
        href = es_link.get_attribute("href")
        assert "page=" not in href
