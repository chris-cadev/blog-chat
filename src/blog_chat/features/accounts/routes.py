import secrets

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from blog_chat.core.database import get_db
from blog_chat.core.logging import log_business_event
from blog_chat.core.responses import create_templates
from blog_chat.features.accounts.models import User
from blog_chat.features.accounts.services import (
    assign_username,
    create_token,
    get_user_id_from_cookie,
    get_alias_from_token,
    decode_token,
)

router = APIRouter()

templates = create_templates("src/blog_chat/features/accounts/templates")


@router.post("/api/set-username")
async def set_username(request: Request, db: AsyncSession = Depends(get_db)):
    content_type = request.headers.get("Content-Type", "")

    if "application/json" in content_type:
        data = await request.json()
        alias = str(data.get("username", "")).strip()
        wants_json = True
    else:
        form = await request.form()
        alias = str(form.get("username", "")).strip()
        wants_json = False

    if not alias or len(alias) > 50:
        if wants_json:
            return JSONResponse({"error": "invalid_alias", "message": "Nombre inválido. Usa 1-50 caracteres."}, status_code=400)
        html = templates.env.get_template(
            "invalid_user.html"
        ).render()
        return HTMLResponse(html, status_code=400)

    client_ip = request.client.host if request.client else None

    # resolve current_user_id from cookie (sub) or legacy username fallback
    current_user_id = get_user_id_from_cookie(request)
    if current_user_id is None:
        # legacy token: try to map alias in token to user id
        token = request.cookies.get("chat_token", "")
        payload = decode_token(token) if token else None
        legacy_alias = None
        if payload:
            legacy_alias = payload.get("alias") or payload.get("username")
        if legacy_alias:
            row = (await db.execute(
                select(User).where((User.alias == legacy_alias) | (User.username == legacy_alias))
            )).scalar_one_or_none()
            if row:
                current_user_id = str(row.id)

    result = await assign_username(db, alias, current_user_id, client_ip)

    if result == "taken":
        suggestion = f"{alias}-{secrets.randbelow(900)+100}"
        log_business_event(
            "account.username_conflict",
            "Alias taken",
            alias=alias,
            result="taken",
        )
        if wants_json:
            return JSONResponse(
                {"error": "alias_taken", "message": f"El nombre {alias} ya está en uso.", "suggestion": suggestion},
                status_code=409,
            )
        html = templates.env.get_template("alias_taken.html").render(requested=alias, suggestion=suggestion)
        return HTMLResponse(html, status_code=409)

    if result == "invalid":
        if wants_json:
            return JSONResponse({"error": "invalid_alias", "message": "Nombre inválido."}, status_code=400)
        html = templates.env.get_template("invalid_user.html").render()
        return HTMLResponse(html, status_code=400)

    # ok -> fetch user to get its id for token
    user = (await db.execute(select(User).where(User.alias == alias))).scalar_one_or_none()
    # fallback if somehow not found (race), use current_user_id
    user_id = str(user.id) if user else (current_user_id or alias)
    user_alias = user.alias if user else alias

    # determine previous for logging
    previous_alias = None
    token_prev = request.cookies.get("chat_token", "")
    if token_prev:
        previous_alias = get_alias_from_token(token_prev)

    log_business_event(
        "account.username_changed",
        "Username changed",
        username=user_alias,
        previous_username=previous_alias,
        user_id=user_id,
    )

    token = create_token(user_id, user_alias)

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
