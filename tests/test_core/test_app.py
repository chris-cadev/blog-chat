import re

from fastapi.testclient import TestClient

from blog_chat.app import app, build_csp, FRAME_SRC_ALLOWLIST


class TestCSPTemplate:
    def test_frame_src_includes_nonce_placeholder(self):
        csp = build_csp("test-nonce-123")
        assert "frame-src 'nonce-test-nonce-123'" in csp

    def test_frame_src_includes_allowed_hosts(self):
        csp = build_csp("test-nonce-123")
        for host in FRAME_SRC_ALLOWLIST:
            assert host in csp

    def test_default_src_is_self(self):
        csp = build_csp("test-nonce-123")
        assert "default-src 'self'" in csp

    def test_object_src_is_none(self):
        csp = build_csp("test-nonce-123")
        assert "object-src 'none'" in csp

    def test_frame_ancestors_is_none(self):
        csp = build_csp("test-nonce-123")
        assert "frame-ancestors 'none'" in csp

    def test_default_script_src_is_self(self):
        csp = build_csp("test-nonce-123")
        assert "script-src 'self'" in csp

    def test_default_connect_src_is_self_and_websockets(self):
        csp = build_csp("test-nonce-123")
        assert "connect-src 'self' wss: ws:" in csp


class TestPostPage:
    def test_iframe_nonce_matches_csp_nonce(self):
        with TestClient(app) as client:
            response = client.get("/en/firstcommit")
            assert response.status_code == 200

            csp = response.headers.get("content-security-policy")
            csp_nonce = re.search(r"nonce-([A-Za-z0-9_-]+)", csp)
            assert csp_nonce, "expected a nonce in the CSP frame-src"

            iframe = re.search(r"<iframe[^>]*>", response.text)
            assert iframe, "expected an iframe in the post content"

            iframe_nonce = re.search(r'nonce="?([A-Za-z0-9_-]+)"?', iframe.group(0))
            assert iframe_nonce, "expected a nonce on the iframe"

            assert iframe_nonce.group(1) == csp_nonce.group(1)

    def test_iframe_src_is_allowlisted(self):
        with TestClient(app) as client:
            response = client.get("/en/firstcommit")
            csp = response.headers.get("content-security-policy")
            assert "https://firstcommit.debugchris.com" in csp

    def _page_username(self, client, path="/en/firstcommit"):
        page = client.get(path)
        # new design uses #username-btn (may be minified without quotes), old used font-bold/username-edit-btn
        for pat in [
            r'id="?username-btn"?[^>]*>([^<]+)<',
            r'id="?username-edit-btn"?[^>]*>([^<]+)<',
            r'font-bold[^>]*>([^<]+)<',
        ]:
            match = re.search(pat, page.text)
            if match:
                v = match.group(1).strip()
                if v:
                    return v
        return None

    def test_auto_assigns_guest_identity(self):
        with TestClient(app) as client:
            response = client.get("/en/firstcommit")
            assert response.status_code == 200
            assert response.cookies.get("chat_token")
            assert 'username-btn' in response.text
            assert 'placeholder="Enter your name"' not in response.text
            name = self._page_username(client, "/en/firstcommit")
            assert name
            assert re.fullmatch(r"[A-Z][a-z]+[A-Z][a-z]+-\d{4}", name)

    def test_guest_identity_persists_across_requests(self):
        with TestClient(app) as client:
            first = self._page_username(client, "/en/firstcommit")
            second = self._page_username(client, "/en/firstcommit")
            assert first == second
            assert first

    def test_change_username_after_auto_identity(self):
        import secrets as _secrets
        unique = f"CustomName-{_secrets.randbelow(9000)+1000}"
        with TestClient(app) as client:
            self._page_username(client, "/en/firstcommit")
            response = client.post(
                "/api/set-username?room=firstcommit",
                data={"username": unique, "room": "firstcommit"},
            )
            assert response.status_code == 200
            assert self._page_username(client, "/en/firstcommit") == unique

    def test_interaction_hints_render(self):
        with TestClient(app) as client:
            response = client.get("/en/firstcommit")
            assert response.status_code == 200
            assert "chat-input-group" in response.text
            assert "chat-input-hint" in response.text
            assert "starter-prompts" in response.text
            assert "data-starter" in response.text
            assert "(Enter to send)" not in response.text

            index = client.get("/en/")
            assert "starter-prompts" in index.text
