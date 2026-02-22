import asyncio
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Set

from fastapi.concurrency import asynccontextmanager
import jwt
import markdown
import powerwalk
import yaml
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import async_session_maker, init_db, User, Message, get_db
from .weather import fetch_weather_by_ip

CONTENT_DIR = Path("content")

JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"


def parse_markdown_file(file_path: Path) -> dict | None:
    content = file_path.read_text(encoding="utf-8")

    frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)

    if frontmatter_match:
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
        body = content[frontmatter_match.end():]
    else:
        frontmatter = {}
        body = content

    return {
        "title": frontmatter.get("title", file_path.stem),
        "slug": frontmatter.get("slug", file_path.stem),
        "tags": frontmatter.get("tags", []),
        "created": frontmatter.get("created", ""),
        "updated": frontmatter.get("updated", ""),
        "content": body.strip(),
    }


def get_posts() -> list[dict]:
    posts = []
    for entry in powerwalk.walk(CONTENT_DIR, filter="**/*.md"):
        post = parse_markdown_file(entry.path)
        if post:
            posts.append(post)
    return sorted(posts, key=lambda p: p.get("created", ""), reverse=True)


def get_post(slug: str) -> dict | None:
    for entry in powerwalk.walk(CONTENT_DIR, filter="**/*.md"):
        post = parse_markdown_file(entry.path)
        if post and post.get("slug") == slug:
            return post
    return None


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

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="src/blog_chat/templates")
templates.env.filters["markdown"] = lambda text: markdown.markdown(text or "")


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = set()
        self.active_connections[room].add(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections:
            self.active_connections[room].discard(websocket)

    async def broadcast(self, message: dict, room: str):
        if room in self.active_connections:
            for connection in self.active_connections[room]:
                await connection.send_json(message)

    async def broadcast_weather_update(self, message_id: int, weather: str, room: str):
        await self.broadcast({
            "type": "weather_update",
            "message_id": message_id,
            "weather": weather
        }, room)


manager = ConnectionManager()


@app.get("/")
def read_root(request: Request):
    posts = get_posts()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts, "room": "offtopic"})


@app.get("/{slug}")
def read_item(request: Request, slug: str):
    post = get_post(slug)
    if not post:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "posts": get_posts(), "error": "Post not found"},
            status_code=404,
        )
    return templates.TemplateResponse("post.html", {"request": request, "post": post, "room": slug})


@app.post("/api/set-username")
async def set_username(request: Request, db: AsyncSession = Depends(get_db)):
    is_htmx = request.headers.get("HX-Request") == "true"
    content_type = request.headers.get("Content-Type", "")

    if "application/json" in content_type:
        data = await request.json()
        username = data.get("username", "").strip()
    else:
        form = await request.form()
        username = str(form.get("username", "")).strip()

    if not username or len(username) > 50:
        if is_htmx:
            return HTMLResponse("<div hx-swap-oob='true' id='username-section'></div>", status_code=400)
        return JSONResponse({"error": "Invalid username"}, status_code=400)

    client_ip = request.client.host if request.client else None

    existing = await db.execute(select(User).where(User.username == username))
    existing_user = existing.scalar_one_or_none()

    if not existing_user:
        new_user = User(username=username, ip_address=client_ip)
        db.add(new_user)
        await db.commit()

    payload = {
        "username": username,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    if is_htmx:
        response = HTMLResponse("<div id='username-section'></div>")
        response.set_cookie(
            key="chat_token",
            value=token,
            httponly=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 30
        )
        return response

    response = JSONResponse({"token": token, "username": username})
    response.set_cookie(
        key="chat_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30
    )
    return response


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    room = websocket.query_params.get("room", "offtopic")
    await manager.connect(websocket, room)

    token = websocket.query_params.get("token", "")
    username = "Guest"

    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            username = payload.get("username", "Guest")
        except jwt.ExpiredSignatureError:
            username = "Guest"
        except jwt.InvalidTokenError:
            username = "Guest"

    result = await db.execute(
        select(Message)
        .where(Message.room_slug == room)
        .order_by(Message.timestamp.desc())
        .limit(50)
    )
    messages = result.scalars().all()
    messages_list = [
        {
            "id": m.id,
            "username": m.username,
            "content": m.content,
            "timestamp": m.timestamp.isoformat(),
            "weather": m.weather,
        }
        for m in reversed(messages)
    ]
    await websocket.send_json({"type": "history", "messages": messages_list})

    try:
        while True:
            data = await websocket.receive_text()
            message_text = data.strip()

            if not message_text:
                continue

            client_ip = websocket.client.host if websocket.client else None

            new_message = Message(
                room_slug=room,
                username=username,
                content=message_text,
                ip_address=client_ip,
            )
            db.add(new_message)
            await db.commit()
            await db.refresh(new_message)

            message_payload = {
                "type": "message",
                "id": new_message.id,
                "username": username,
                "content": message_text,
                "timestamp": new_message.timestamp.isoformat(),
                "weather": None,
            }
            await manager.broadcast(message_payload, room)

            asyncio.create_task(
                update_weather(
                    new_message.id,
                    room,
                    client_ip
                )
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket, room)


async def update_weather(message_id: int, room: str, ip_address: str | None):
    if not ip_address:
        return

    await asyncio.sleep(2)

    weather = await fetch_weather_by_ip(ip_address)
    if weather:
        async with async_session_maker() as db:
            result = await db.execute(select(Message).where(Message.id == message_id))
            message = result.scalar_one_or_none()
            if message:
                message.weather = weather
                await db.commit()
                await manager.broadcast_weather_update(message_id, weather, room)
