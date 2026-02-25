from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from blog_chat.core.database import get_db
from blog_chat.core.responses import create_templates
from blog_chat.features.accounts.models import User
from blog_chat.features.accounts.services import create_token

router = APIRouter()

templates = create_templates("src/blog_chat/features/accounts/templates")


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
        html = templates.env.get_template(
            "invalid_user.html"
        ).render()
        return HTMLResponse(html, status_code=400)

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
        "connected_user.html"
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
    html = templates.env.get_template(
        "cleared_user.html"
    ).render()
    response = HTMLResponse(html)
    response.set_cookie(
        key="chat_token",
        value="",
        httponly=True,
        samesite="lax",
        max_age=0
    )
    return response
