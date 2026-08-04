from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import asyncio
import humanize
import json

from blog_chat.core.database import get_db, engine, init_db
from blog_chat.core.db_watcher import DatabaseChangeWatcher, sqlite_db_path
from blog_chat.core.filters import add_filter, add_markdown_filter
from blog_chat.core.logging import get_logger, log_business_event
from blog_chat.core.responses import create_templates
from blog_chat.features.chat.models import Message
from blog_chat.features.chat.services import get_or_create_user_id, resolve_user_id
from blog_chat.features.chat.websocket import ConnectionManager
from blog_chat.features.accounts.services import get_username_from_token

router = APIRouter()

manager = ConnectionManager()

logger = get_logger("chat")

templates = create_templates("src/blog_chat/features/chat/templates")
add_markdown_filter(templates)

MAX_MESSAGE_LENGTH = 280
HEARTBEAT_INTERVAL = 30
CONTROL_TYPES = {"sync"}


async def load_history(db: AsyncSession, room: str, username: str, timezone_name: str | None) -> list[dict]:
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.user))
        .where(Message.room_slug == room)
        .order_by(Message.timestamp.desc())
        .limit(50)
    )
    messages = result.scalars().all()
    current_user_id = await resolve_user_id(db, username)
    messages_list = []
    for m in messages:
        display_name = m.user.username if m.user is not None else m.username
        is_own = (m.user_id is not None and m.user_id == current_user_id) \
            or m.username == username
        html = render_message_template(
            display_name, m.content, m.timestamp.isoformat(), is_own,
            show_header=True, timezone_name=timezone_name)
        messages_list.append({
            "id": m.id,
            "html": html,
            "username": display_name,
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
    hash_value = 0x811C9DC5
    for byte in username.encode("utf-8"):
        hash_value ^= byte
        hash_value = (hash_value * 0x01000193) & 0xFFFFFFFF
    hue = hash_value % 360
    return f"hsl({hue}, 70%, 45%)"


add_filter(templates, "username_color", get_username_color)


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
        logger.warning(
            "chat.connect.rejected",
            extra={
                "event": "chat.connect.rejected",
                "room": room,
                "username": username,
                "detail": "ops",
            },
        )
        return

    logger.info(
        "chat.user.joined",
        extra={"event": "chat.user.joined", "room": room, "username": username, "detail": "ops"},
    )

    await websocket.send_json({
        "type": "history",
        "messages": await load_history(db, room, username, timezone_name),
    })

    try:
        await manager.broadcast_presence(room)

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
                logger.warning(
                    "chat.message.rejected",
                    extra={
                        "event": "chat.message.rejected",
                        "room": room,
                        "username": username,
                        "reason": "too_long",
                        "detail": "ops",
                    },
                )
                await websocket.send_json({
                    "type": "error",
                    "message": f"Message too long. Maximum {MAX_MESSAGE_LENGTH} characters allowed."
                })
                continue

            if manager.rate_limited(websocket):
                logger.warning(
                    "chat.message.rejected",
                    extra={
                        "event": "chat.message.rejected",
                        "room": room,
                        "username": username,
                        "reason": "rate_limited",
                        "detail": "ops",
                    },
                )
                await websocket.send_json({
                    "type": "error",
                    "message": "You are sending messages too quickly. Please wait a moment."
                })
                continue

            client_ip = websocket.client.host if websocket.client else None

            user_id = await get_or_create_user_id(db, username, client_ip)

            new_message = Message(
                room_slug=room,
                username=username,
                content=message_text,
                ip_address=client_ip,
                user_id=user_id,
            )
            db.add(new_message)
            await db.commit()
            await db.refresh(new_message)
            db_watcher.note_internal_change()

            log_business_event(
                "chat.message.sent",
                "Chat message sent",
                room=room,
                username=username,
                message_id=new_message.id,
            )

            timestamp_iso = new_message.timestamp.isoformat()

            async def make_payload(
                recipient_username: str,
                recipient_timezone: str | None,
            ) -> dict:
                recipient_user_id = await resolve_user_id(db, recipient_username)
                is_own = (
                    new_message.user_id is not None
                    and new_message.user_id == recipient_user_id
                ) or new_message.username == recipient_username
                html = render_message_template(
                    new_message.username,
                    new_message.content,
                    timestamp_iso,
                    is_own,
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
        pass
    finally:
        manager.disconnect(websocket, room)
        await manager.broadcast_presence(room)
        logger.info(
            "chat.user.left",
            extra={"event": "chat.user.left", "room": room, "username": username, "detail": "ops"},
        )
