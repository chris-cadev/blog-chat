from pathlib import Path

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from blog_chat.core.database import get_db
from blog_chat.core.responses import create_templates
from blog_chat.features.chat.models import User, Message
from blog_chat.features.chat.websocket import ConnectionManager
from blog_chat.features.chat.services import create_token, get_username_from_token

router = APIRouter()

manager = ConnectionManager()

templates = create_templates("src/blog_chat/features/chat/templates")


@router.post("/api/set-username")
async def set_username(request: Request, db: AsyncSession = Depends(get_db)):
    content_type = request.headers.get("Content-Type", "")

    if "application/json" in content_type:
        data = await request.json()
        username = data.get("username", "").strip()
    else:
        form = await request.form()
        username = str(form.get("username", "")).strip()

    if not username or len(username) > 50:
        return HTMLResponse("<div id='username-section'>Invalid username</div>", status_code=400)

    client_ip = request.client.host if request.client else None

    existing = await db.execute(select(User).where(User.username == username))
    existing_user = existing.scalar_one_or_none()

    if not existing_user:
        new_user = User(username=username, ip_address=client_ip)
        db.add(new_user)
        await db.commit()

    token = create_token(username)

    room = request.query_params.get("room", "offtopic")
    connected_html = templates.env.get_template(
        "ws_connected.html"
    ).render(room=room, token=token)

    response = HTMLResponse(connected_html)
    response.set_cookie(
        key="chat_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30
    )
    return response


@router.post("/api/clear-username")
async def clear_username(request: Request):
    response = HTMLResponse(
        "<div id='username-section'>Username cleared</div>")
    response.set_cookie(
        key="chat_token",
        value="",
        httponly=True,
        samesite="lax",
        max_age=0
    )
    return response


@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    room = websocket.query_params.get("room", "offtopic")
    await manager.connect(websocket, room)

    token = websocket.cookies.get("chat_token", "")
    username = get_username_from_token(token)

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
                "username": new_message.username,
                "content": new_message.content,
                "timestamp": new_message.timestamp.isoformat(),
            }
            await manager.broadcast(message_payload, room)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
