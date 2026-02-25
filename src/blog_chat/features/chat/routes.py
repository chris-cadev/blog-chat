from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import hashlib
import humanize

from blog_chat.core.database import get_db
from blog_chat.core.filters import add_markdown_filter
from blog_chat.core.responses import create_templates
from blog_chat.features.chat.models import Message
from blog_chat.features.chat.websocket import ConnectionManager
from blog_chat.features.accounts.services import get_username_from_token

router = APIRouter()

manager = ConnectionManager()
user_timezones: dict[str, str] = {}

templates = create_templates("src/blog_chat/features/chat/templates")
add_markdown_filter(templates)

MAX_MESSAGE_LENGTH = 280


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


@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    room = websocket.query_params.get("room", "offtopic")
    await manager.connect(websocket, room)

    token = websocket.cookies.get("chat_token", "")
    username = get_username_from_token(token)

    result = await db.execute(
        select(Message)
        .where(Message.room_slug == room)
        .order_by(Message.timestamp.asc())
        .limit(50)
    )
    messages = result.scalars().all()
    messages_list = []
    timezone_name = websocket.cookies.get("chat_timezone")
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

    await websocket.send_json({"type": "history", "messages": messages_list})

    try:
        while True:
            data = await websocket.receive_text()
            
            timezone_name = user_timezones.get(room) or websocket.cookies.get("chat_timezone")
            message_text = data.strip()
            
            if message_text.startswith("tz:"):
                parts = message_text.split("|", 1)
                if len(parts) == 2 and parts[0].startswith("tz:"):
                    timezone_name = parts[0][3:]
                    message_text = parts[1].strip()
                    user_timezones[room] = timezone_name

            if not message_text:
                continue

            if len(message_text) > MAX_MESSAGE_LENGTH:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Message too long. Maximum {MAX_MESSAGE_LENGTH} characters allowed."
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

            html = render_message_template(
                new_message.username,
                new_message.content,
                new_message.timestamp.isoformat(),
                True,
                show_header=True,
                timezone_name=timezone_name
            )
            message_payload = {
                "type": "message",
                "id": new_message.id,
                "html": html,
                "username": new_message.username,
                "timestamp": new_message.timestamp.isoformat(),
            }
            await manager.broadcast(message_payload, room)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
