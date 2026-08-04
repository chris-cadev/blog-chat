import re

from fastapi.testclient import TestClient

from blog_chat.app import app, CSP_TEMPLATE, FRAME_SRC_ALLOWLIST


class TestCSPTemplate:
    def test_frame_src_includes_nonce_placeholder(self):
        csp = CSP_TEMPLATE.format(nonce="test-nonce-123")
        assert "frame-src 'nonce-test-nonce-123'" in csp

    def test_frame_src_includes_allowed_hosts(self):
        csp = CSP_TEMPLATE.format(nonce="test-nonce-123")
        for host in FRAME_SRC_ALLOWLIST:
            assert host in csp

    def test_default_src_is_self(self):
        csp = CSP_TEMPLATE.format(nonce="test-nonce-123")
        assert "default-src 'self'" in csp

    def test_object_src_is_none(self):
        csp = CSP_TEMPLATE.format(nonce="test-nonce-123")
        assert "object-src 'none'" in csp

    def test_frame_ancestors_is_none(self):
        csp = CSP_TEMPLATE.format(nonce="test-nonce-123")
        assert "frame-ancestors 'none'" in csp


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
