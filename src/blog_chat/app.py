import secrets
import contextvars

from blog_chat.features.chat.routes import router as chat_router
from blog_chat.features.posts.routes import router as posts_router
from blog_chat.features.accounts.routes import router as accounts_router
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi import FastAPI, Request
from blog_chat.core.database import init_db
from blog_chat.core.responses import create_templates

CSP_NONCE: contextvars.ContextVar[str] = contextvars.ContextVar("csp_nonce")

FRAME_SRC_ALLOWLIST = [
    "https://www.youtube.com",
    "https://www.youtube-nocookie.com",
    "https://w.soundcloud.com",
    "https://firstcommit.debugchris.com",
]

CSP_TEMPLATE = "; ".join([
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "connect-src 'self' wss: ws:",
    "font-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    f"frame-src 'nonce-{{nonce}}' {' '.join(FRAME_SRC_ALLOWLIST)}",
])


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        nonce = secrets.token_urlsafe(16)
        token = CSP_NONCE.set(nonce)
        try:
            response = await call_next(request)
            response.headers["Content-Security-Policy"] = CSP_TEMPLATE.format(nonce=nonce)
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            return response
        finally:
            CSP_NONCE.reset(token)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost"],
    allow_methods=["GET", "POST"],
)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(accounts_router)
app.include_router(posts_router)
app.include_router(chat_router)
