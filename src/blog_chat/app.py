import secrets
import contextvars

from blog_chat.features.chat.routes import router as chat_router
from blog_chat.features.chat.routes import db_watcher
from blog_chat.features.posts.routes import router as posts_router
from blog_chat.features.accounts.routes import router as accounts_router
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi import FastAPI, Request
from blog_chat.core.config import UMAMI_ACTIVE, UMAMI_HOST
from blog_chat.core.database import init_db
from blog_chat.core.logging import configure_logging, get_logger
from blog_chat.core.responses import create_templates
from blog_chat.core.tracing import TraceabilityMiddleware
from blog_chat.core.analytics import router as analytics_router

configure_logging()

CSP_NONCE: contextvars.ContextVar[str] = contextvars.ContextVar("csp_nonce")

FRAME_SRC_ALLOWLIST = [
    "https://www.youtube.com",
    "https://www.youtube-nocookie.com",
    "https://w.soundcloud.com",
    "https://firstcommit.debugchris.com",
]

CSP_TEMPLATE = "; ".join([
    "default-src 'self'",
    "script-src {script_src}",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "connect-src {connect_src}",
    "font-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "frame-src 'nonce-{nonce}' " + " ".join(FRAME_SRC_ALLOWLIST),
])


def build_csp(nonce: str) -> str:
    script_src = "'self'"
    connect_src = "'self' wss: ws:"
    if UMAMI_ACTIVE and UMAMI_HOST:
        umami_origin = f"https://{UMAMI_HOST}"
        script_src = f"'self' {umami_origin}"
        connect_src = f"'self' wss: ws: {umami_origin}"
    return CSP_TEMPLATE.format(
        nonce=nonce,
        script_src=script_src,
        connect_src=connect_src,
    )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        nonce = secrets.token_urlsafe(16)
        token = CSP_NONCE.set(nonce)
        try:
            response = await call_next(request)
            response.headers["Content-Security-Policy"] = build_csp(nonce)
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            return response
        finally:
            CSP_NONCE.reset(token)


@asynccontextmanager
async def lifespan(_: FastAPI):
    app_logger = get_logger("app")
    app_logger.info("app.startup", extra={"event": "app.startup"})
    await init_db()
    db_watcher.start()
    try:
        yield
    finally:
        await db_watcher.stop()
        app_logger.info("app.shutdown", extra={"event": "app.shutdown"})


app = FastAPI(lifespan=lifespan)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost"],
    allow_methods=["GET", "POST"],
)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(TraceabilityMiddleware)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(accounts_router)
app.include_router(posts_router)
app.include_router(chat_router)
app.include_router(analytics_router)
