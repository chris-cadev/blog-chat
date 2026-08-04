
from datetime import timedelta
import secrets

import jwt
from fastapi import Request
from coolname import generate as generate_coolname
from sqlalchemy import select

from blog_chat.core.config import JWT_ALGORITHM, JWT_SECRET
from blog_chat.core.base import Base
from blog_chat.features.accounts.models import User


async def assign_username(
    db,
    username: str,
    old_username: str | None,
    ip: str | None,
) -> None:
    existing = (await db.execute(
        select(User).where(User.username == username)
    )).scalar_one_or_none()
    if existing is not None:
        return
    if old_username and old_username != username:
        old_user = (await db.execute(
            select(User).where(User.username == old_username)
        )).scalar_one_or_none()
        if old_user is not None:
            old_user.username = username
            await db.commit()
            return
    db.add(User(username=username, ip_address=ip))
    await db.commit()


def generate_guest_name() -> str:
    words = generate_coolname(2)
    base = "".join(word.capitalize() for word in words)
    suffix = secrets.randbelow(9000) + 1000
    return f"{base}-{suffix}"


def create_token(username: str) -> str:
    payload = {
        "username": username,
        "exp": Base.now() + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_username_from_token(token: str) -> str:
    payload = decode_token(token)
    if payload:
        return payload.get("username", "Guest")
    return "Guest"


def get_username_from_cookie(request: Request) -> str | None:
    token = request.cookies.get("chat_token")
    if token:
        payload = decode_token(token)
        if payload:
            return payload.get("username")
    return None
