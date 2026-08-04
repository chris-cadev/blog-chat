import json
import logging
import sys
from datetime import datetime, timezone

from blog_chat.core.config import APP_ENV, LOG_FORMAT, LOG_LEVEL

SERVICE = "blog_chat"

_RESERVED_EXTRA = frozenset({
    "ts", "level", "logger", "message", "service", "env",
})


def _iso8601(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": _iso8601(record.created),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": SERVICE,
            "env": APP_ENV,
        }
        for key, value in record.__dict__.items():
            if key in _RESERVED_EXTRA or key.startswith("_"):
                continue
            if key in ("args", "exc_info", "exc_text", "stack_info", "msg", "name"):
                continue
            payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)
        return json.dumps(payload, default=str)


class ConsoleFormatter(logging.Formatter):
    _LEVEL_COLORS = {
        "DEBUG": "\x1b[38;5;245m",
        "INFO": "\x1b[38;5;114m",
        "WARNING": "\x1b[38;5;221m",
        "ERROR": "\x1b[38;5;203m",
        "CRITICAL": "\x1b[38;5;196m",
    }
    _RESET = "\x1b[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self._LEVEL_COLORS.get(record.levelname, "")
        level = f"{color}{record.levelname:<8}{self._RESET}"
        request_id = record.__dict__.get("request_id")
        request_id = f" [{request_id}]" if request_id else ""
        message = record.getMessage()
        if record.exc_info:
            message = f"{message}\n{self.formatException(record.exc_info)}"
        extras = []
        for key, value in record.__dict__.items():
            if key in _RESERVED_EXTRA or key.startswith("_") or key in (
                "args", "exc_info", "exc_text", "stack_info", "msg", "name",
                "request_id", "created", "msecs", "relativeCreated", "levelno",
                "levelname", "pathname", "filename", "module", "lineno", "funcName",
                "process", "thread", "threadName",
            ):
                continue
            extras.append(f"{key}={value}")
        extras = f" {chr(32).join(extras)}" if extras else ""
        return (
            f"{_iso8601(record.created)} {level} {record.name}{request_id} "
            f"{message}{extras}"
        )


class RequestContextFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        from blog_chat.core.tracing import TRACE_CONTEXT

        self._get_context = lambda: TRACE_CONTEXT

    def filter(self, record: logging.LogRecord) -> bool:
        context = self._get_context().get({})
        for key, value in context.items():
            if getattr(record, key, None) is None:
                setattr(record, key, value)
        return True


def configure_logging() -> None:
    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)

    formatter: logging.Formatter
    if LOG_FORMAT == "json":
        formatter = JsonFormatter()
    else:
        formatter = ConsoleFormatter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestContextFilter())

    root.handlers = [handler]
    root.propagate = False

    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.error").handlers = []
    logging.getLogger("uvicorn.access").propagate = False
    logging.getLogger("uvicorn").propagate = True
    logging.getLogger("uvicorn.error").propagate = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"{SERVICE}.{name}")


def log_business_event(event: str, message: str, **fields) -> None:
    extra = {"event": event, "detail": "business"}
    extra.update(fields)
    get_logger("events").info(message, extra=extra)
