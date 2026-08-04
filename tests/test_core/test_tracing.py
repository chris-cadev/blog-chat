import logging

from fastapi.testclient import TestClient

from blog_chat.app import app


class TestTraceabilityMiddleware:
    def test_response_has_generated_request_id(self):
        with TestClient(app) as client:
            resp = client.get("/robots.txt")
        request_id = resp.headers.get("x-request-id")
        assert request_id and len(request_id) == 16

    def test_accepts_inbound_request_id(self):
        with TestClient(app) as client:
            resp = client.get("/robots.txt", headers={"X-Request-ID": "custom-id-123"})
        assert resp.headers["x-request-id"] == "custom-id-123"

    def test_logs_request_complete(self, caplog):
        with caplog.at_level(logging.INFO, logger="blog_chat.http"):
            with TestClient(app) as client:
                client.get("/en/")
        matches = [
            r for r in caplog.records
            if getattr(r, "event", None) == "http.request.complete"
        ]
        assert matches
        record = matches[0]
        assert record.method == "GET"
        assert record.path == "/en/"
        assert record.status == 200
        assert record.duration_ms >= 0
        assert record.request_id
        assert record.detail == "ops"

    def test_request_id_links_business_and_http_records(self, caplog):
        with caplog.at_level(logging.INFO, logger="blog_chat"):
            with TestClient(app) as client:
                client.get("/en/")
        http = next(
            r for r in caplog.records
            if getattr(r, "event", None) == "http.request.complete"
        )
        page_view = next(
            r for r in caplog.records
            if getattr(r, "event", None) == "page.view"
        )
        assert http.request_id == page_view.request_id
