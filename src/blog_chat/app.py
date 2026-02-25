from blog_chat.features.chat.routes import router as chat_router
from blog_chat.features.posts.routes import router as posts_router
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi import FastAPI
from blog_chat.core.database import init_db
from blog_chat.core.responses import create_templates


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost"],
    allow_methods=["GET", "POST"],
)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(posts_router)
app.include_router(chat_router)
