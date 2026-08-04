import contextvars
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from blog_chat.core.logging import get_logger

TRACE_CONTEXT: contextvars.ContextVar[dict] = contextvars.ContextVar("trace_context", default={})

REQUEST_ID_HEADER = "X-Request-ID"

logger = get_logger("http")


def get_request_id() -> str:
    return TRACE_CONTEXT.get({}).get("request_id", "")


def set_request_id(request_id: str) -> None:
    TRACE_CONTEXT.set({"request_id": request_id})


class TraceabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex[:16]
        token = TRACE_CONTEXT.set({"request_id": request_id})
        start = time.perf_counter()

        username = None
        try:
            from blog_chat.features.accounts.services import get_username_from_cookie
            username = get_username_from_cookie(request)
        except Exception:
            username = None

        base = {
            "request_id": request_id,
            "event": "http.request.start",
            "method": request.method,
            "path": request.url.path,
            "detail": "ops",
        }
        if request.client:
            base["client_ip"] = request.client.host
        if username:
            base["username"] = username

        logger.debug("http.request.start", extra=base)

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(
                "http.request.error",
                extra={
                    **base,
                    "event": "http.request.error",
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                    "exception_type": type(exc).__name__,
                },
                exc_info=True,
            )
            raise
        finally:
            TRACE_CONTEXT.reset(token)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        user_agent = request.headers.get("user-agent")
        complete = {
            **base,
            "event": "http.request.complete",
            "status": response.status_code,
            "duration_ms": duration_ms,
        }
        if user_agent:
            complete["user_agent"] = user_agent
        log = logger.info if response.status_code < 500 else logger.error
        log("http.request.complete", extra=complete)

        response.headers[REQUEST_ID_HEADER] = request_id
        return response
