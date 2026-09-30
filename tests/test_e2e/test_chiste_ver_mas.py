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


class TestChisteLagañasVerMas:
    def test_ver_mas_reveals_punchline(self, page, live_server):
        page.goto(f"{live_server}/es/chiste-lagañas-ojos")

        ver_mas = page.locator("#fb-more")
        assert ver_mas.is_visible()

        hidden = page.locator("#fb-hidden")
        assert not hidden.is_visible()

        ver_mas.click()

        assert hidden.is_visible()
        assert "Lagañas :3" in hidden.text_content()
        assert ver_mas.count() == 0
