
from datetime import timedelta
import secrets
import uuid
from typing import Literal

import jwt
from fastapi import Request
from coolname import generate as generate_coolname
from sqlalchemy import select

from blog_chat.core.config import JWT_ALGORITHM, JWT_SECRET
from blog_chat.core.base import Base
from blog_chat.features.accounts.models import User


AssignResult = Literal["ok", "taken", "invalid"]


def _is_uuid_like(v: str) -> bool:
    return len(v) == 36 and v.count("-") == 4

async def assign_username(
    db,
    requested_alias: str,
    current_user_id: str | None,
    ip: str | None,
) -> AssignResult:
    alias = requested_alias.strip()
    if not alias or len(alias) > 50:
        return "invalid"
    # legacy compat: if current_user_id looks like an alias (not uuid), resolve it
    if current_user_id is not None and not _is_uuid_like(str(current_user_id)):
        # treat as old_alias -> lookup id
        old = (await db.execute(
            select(User).where((User.alias == current_user_id) | (User.username == current_user_id))
        )).scalar_one_or_none()
        if old is not None:
            current_user_id = str(old.id)
        else:
            # old alias not found -> treat as no current user (new registration)
            current_user_id = None
    # alias taken by someone else?
    existing = (await db.execute(
        select(User).where(User.alias == alias)
    )).scalar_one_or_none()
    if existing is not None:
        if current_user_id is not None and str(existing.id) == str(current_user_id):
            return "ok"
        return "taken"
    # also block if alias collides with immutable username of another user (defense in depth)
    existing_username = (await db.execute(
        select(User).where(User.username == alias)
    )).scalar_one_or_none()
    if existing_username is not None:
        if current_user_id is not None and str(existing_username.id) == str(current_user_id):
            # same user owns that username (first alias == username), allow rename to itself
            if existing_username.alias == alias:
                return "ok"
        else:
            return "taken"

    if current_user_id:
        user = await db.get(User, current_user_id)
        if user is not None:
            user.alias = alias
            await db.commit()
            return "ok"
        # token orphan: sub points to non-existent user (e.g. after DB restore)
        # create fresh user with that id
        db.add(User(id=str(current_user_id), username=alias, alias=alias, ip_address=ip))
        await db.commit()
        return "ok"

    # no current user -> new registration
    db.add(User(id=str(uuid.uuid4()), username=alias, alias=alias, ip_address=ip))
    await db.commit()
    return "ok"


# backwards-compat shim: old callers may still pass (username, old_username)
# keep signature flexible via wrapper below for tests not yet migrated
async def assign_username_legacy(db, username: str, old_username: str | None, ip: str | None) -> None:
    # resolve old user id by username/alias
    current_id = None
    if old_username:
        u = (await db.execute(
            select(User).where((User.alias == old_username) | (User.username == old_username))
        )).scalar_one_or_none()
        if u:
            current_id = str(u.id)
    await assign_username(db, username, current_id, ip)


def generate_guest_name() -> str:
    words = generate_coolname(2)
    base = "".join(word.capitalize() for word in words)
    suffix = secrets.randbelow(9000) + 1000
    return f"{base}-{suffix}"


def _core_create_token(user_id: str, alias: str | None = None) -> str:
    payload: dict = {
        "sub": str(user_id),
        "exp": Base.now() + timedelta(days=30),
    }
    if alias:
        payload["alias"] = alias
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _legacy_create_token(username: str) -> str:
    if len(username) == 36 and username.count("-") == 4:
        return _core_create_token(username, None)
    return jwt.encode({"username": username, "alias": username, "exp": Base.now() + timedelta(days=30)}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_token(*args, **kwargs) -> str:
    # dispatch: create_token(user_id, alias) OR create_token(username) legacy OR kwargs
    if "user_id" in kwargs:
        return _core_create_token(str(kwargs["user_id"]), kwargs.get("alias"))
    if "username" in kwargs:
        return _legacy_create_token(kwargs["username"])
    if len(args) == 2:
        return _core_create_token(str(args[0]), str(args[1]) if args[1] else None)
    if len(args) == 1:
        val = str(args[0])
        # heuristic uuid?
        if len(val) == 36 and val.count("-") >= 3:
            return _core_create_token(val, None)
        return _legacy_create_token(val)
    raise TypeError("create_token requires user_id/alias or username")


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_user_id_from_token(token: str) -> str | None:
    payload = decode_token(token)
    if not payload:
        return None
    sub = payload.get("sub")
    if sub:
        return str(sub)
    # fallback: legacy token with username -> will be resolved by caller via DB lookup
    return None


def get_alias_from_token(token: str) -> str | None:
    payload = decode_token(token)
    if not payload:
        return None
    alias = payload.get("alias")
    if alias:
        return str(alias)
    # fallback legacy
    username = payload.get("username")
    if username:
        return str(username)
    return None


def get_username_from_token(token: str) -> str:
    # legacy name kept for compat — returns alias
    alias = get_alias_from_token(token)
    return alias if alias else "Guest"


def get_username_from_cookie(request: Request) -> str | None:
    token = request.cookies.get("chat_token")
    if token:
        alias = get_alias_from_token(token)
        if alias:
            return alias
    return None


def get_user_id_from_cookie(request: Request) -> str | None:
    token = request.cookies.get("chat_token")
    if token:
        uid = get_user_id_from_token(token)
        if uid:
            return uid
        # legacy token: try to resolve username to id via fallback not possible here (no db)
        # return None to signal need for DB lookup
    return None
