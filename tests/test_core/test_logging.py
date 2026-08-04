import json
import logging
import sys

from blog_chat.core.logging import (
    JsonFormatter,
    RequestContextFilter,
    log_business_event,
)
from blog_chat.core.tracing import set_request_id, TRACE_CONTEXT


def _make_record(msg="hello world", level=logging.INFO, extra=None):
    record = logging.LogRecord(
        name="blog_chat.test",
        level=level,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=(),
        exc_info=None,
    )
    if extra:
        for key, value in extra.items():
            setattr(record, key, value)
    return record


class TestJsonFormatter:
    def test_emits_valid_json_with_core_fields(self):
        out = json.loads(JsonFormatter().format(_make_record()))
        assert out["message"] == "hello world"
        assert out["logger"] == "blog_chat.test"
        assert out["level"] == "INFO"
        assert out["service"] == "blog_chat"
        assert out["ts"].endswith("Z")

    def test_includes_extra_fields(self):
        out = json.loads(JsonFormatter().format(_make_record(extra={
            "event": "page.view",
            "status": 200,
            "duration_ms": 12.5,
        })))
        assert out["event"] == "page.view"
        assert out["status"] == 200
        assert out["duration_ms"] == 12.5

    def test_does_not_duplicate_core_fields(self):
        out = json.loads(JsonFormatter().format(_make_record(extra={"level": "x"})))
        assert out["level"] == "INFO"

    def test_formats_exceptions(self):
        try:
            raise ValueError("boom")
        except ValueError:
            record = logging.LogRecord(
                "blog_chat.test", logging.ERROR, __file__, 1, "failed", (), sys.exc_info()
            )
        out = json.loads(JsonFormatter().format(record))
        assert "ValueError: boom" in out["exception"]


class TestRequestContextFilter:
    def test_injects_request_id_from_context(self):
        set_request_id("xyz789")
        try:
            record = _make_record()
            assert RequestContextFilter().filter(record)
            assert record.request_id == "xyz789"
        finally:
            TRACE_CONTEXT.set({})

    def test_leaves_record_alone_when_no_context(self):
        TRACE_CONTEXT.set({})
        record = _make_record()
        RequestContextFilter().filter(record)
        assert getattr(record, "request_id", None) is None


class TestBusinessEvent:
    def test_logs_event_with_detail_and_fields(self, caplog):
        with caplog.at_level(logging.INFO, logger="blog_chat.events"):
            log_business_event("page.view", "Post viewed", slug="hello", lang="en")
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.event == "page.view"
        assert record.detail == "business"
        assert record.slug == "hello"
        assert record.lang == "en"
