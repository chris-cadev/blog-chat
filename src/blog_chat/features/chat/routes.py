from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import markdown

from blog_chat.core.database import get_db
from blog_chat.core.filters import add_markdown_filter
from blog_chat.core.responses import create_templates
from blog_chat.features.chat.models import Message
from blog_chat.features.chat.websocket import ConnectionManager
from blog_chat.features.accounts.services import get_username_from_token

router = APIRouter()

manager = ConnectionManager()

templates = create_templates("src/blog_chat/features/chat/templates")
add_markdown_filter(templates)


def render_message_template(username: str, content: str, timestamp: str, is_own: bool) -> str:
    formatted_time = ""
    if timestamp:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        formatted_time = dt.strftime("%H:%M")

    return templates.get_template("message.html").render(
        username=username,
        content=content,
        timestamp=formatted_time,
        isOwnMessage=is_own
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
    for m in reversed(messages):
        html = render_message_template(
            m.username, m.content, m.timestamp.isoformat(), m.username == username)
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

            html = render_message_template(
                new_message.username,
                new_message.content,
                new_message.timestamp.isoformat(),
                True
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
