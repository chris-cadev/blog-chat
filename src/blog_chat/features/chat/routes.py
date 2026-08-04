from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import asyncio
import hashlib
import humanize
import json

from blog_chat.core.database import get_db, engine, init_db
from blog_chat.core.db_watcher import DatabaseChangeWatcher, sqlite_db_path
from blog_chat.core.filters import add_markdown_filter
from blog_chat.core.responses import create_templates
from blog_chat.features.chat.models import Message
from blog_chat.features.chat.websocket import ConnectionManager
from blog_chat.features.accounts.services import get_username_from_token

router = APIRouter()

manager = ConnectionManager()

templates = create_templates("src/blog_chat/features/chat/templates")
add_markdown_filter(templates)

MAX_MESSAGE_LENGTH = 280
HEARTBEAT_INTERVAL = 30
CONTROL_TYPES = {"sync"}


async def load_history(db: AsyncSession, room: str, username: str, timezone_name: str | None) -> list[dict]:
    result = await db.execute(
        select(Message)
        .where(Message.room_slug == room)
        .order_by(Message.timestamp.asc())
        .limit(50)
    )
    messages = result.scalars().all()
    messages_list = []
    for m in messages:
        html = render_message_template(
            m.username, m.content, m.timestamp.isoformat(), m.username == username,
            show_header=True, timezone_name=timezone_name)
        messages_list.append({
            "id": m.id,
            "html": html,
            "username": m.username,
            "timestamp": m.timestamp.isoformat(),
        })
    return messages_list


async def _handle_db_change():
    path = sqlite_db_path()
    if path is not None and not path.exists():
        await engine.dispose()
        await init_db()
    await manager.broadcast_refresh()
    db_watcher.note_internal_change()


db_watcher = DatabaseChangeWatcher(on_change=_handle_db_change)


def get_username_color(username: str) -> str:
    hash_value = int(hashlib.md5(username.encode()).hexdigest(), 16)
    hue = hash_value % 360
    return f"hsl({hue}, 70%, 45%)"


def format_timestamp(timestamp: str, timezone_name: str | None = None) -> str:
    if not timestamp:
        return ""
    
    ts = timestamp.replace("Z", "+00:00")
    dt_utc = datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
    
    if timezone_name:
        try:
            dt_local = dt_utc.astimezone(ZoneInfo(timezone_name))
            return humanize.naturaltime(dt_local)
        except Exception:
            pass
    
    return humanize.naturaltime(dt_utc)


def render_message_template(username: str, content: str, timestamp: str, is_own: bool, show_header: bool = True, timezone_name: str | None = None) -> str:
    formatted_time = format_timestamp(timestamp, timezone_name)

    return templates.get_template("message.html").render(
        username=username,
        content=content,
        timestamp=formatted_time,
        isOwnMessage=is_own,
        show_header=show_header,
        userColor=get_username_color(username)
    )


def parse_control_message(text: str) -> dict | None:
    if not text.startswith("{"):
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(payload, dict) and payload.get("type") in CONTROL_TYPES:
        return payload
    return None


@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    room = websocket.query_params.get("room", "offtopic")
    token = websocket.cookies.get("chat_token", "")
    username = get_username_from_token(token)
    timezone_name = websocket.cookies.get("chat_timezone")

    if not await manager.connect(websocket, room, username, timezone_name):
        return

    await websocket.send_json({
        "type": "history",
        "messages": await load_history(db, room, username, timezone_name),
    })

    try:
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=HEARTBEAT_INTERVAL,
                )
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "heartbeat"})
                continue

            text = data.strip()
            control = parse_control_message(text)
            if control is not None:
                if control.get("type") == "sync":
                    await websocket.send_json({
                        "type": "history",
                        "messages": await load_history(db, room, username, timezone_name),
                    })
                continue

            message_text = text
            if not message_text:
                continue

            if len(message_text) > MAX_MESSAGE_LENGTH:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Message too long. Maximum {MAX_MESSAGE_LENGTH} characters allowed."
                })
                continue

            if manager.rate_limited(websocket):
                await websocket.send_json({
                    "type": "error",
                    "message": "You are sending messages too quickly. Please wait a moment."
                })
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
            db_watcher.note_internal_change()

            timestamp_iso = new_message.timestamp.isoformat()

            async def make_payload(
                recipient_username: str,
                recipient_timezone: str | None,
            ) -> dict:
                html = render_message_template(
                    new_message.username,
                    new_message.content,
                    timestamp_iso,
                    new_message.username == recipient_username,
                    show_header=True,
                    timezone_name=recipient_timezone,
                )
                return {
                    "type": "message",
                    "id": new_message.id,
                    "html": html,
                    "username": new_message.username,
                    "timestamp": timestamp_iso,
                }

            await manager.broadcast(room, make_payload)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
