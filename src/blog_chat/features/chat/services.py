from sqlalchemy import select

from blog_chat.features.accounts.models import User


async def resolve_user_id(db, alias: str) -> str | None:
    if not alias:
        return None
    # prefer alias, fallback to username for legacy rows
    user = (await db.execute(
        select(User).where((User.alias == alias) | (User.username == alias))
    )).scalar_one_or_none()
    if user is not None:
        return str(user.id)
    return None


async def resolve_user_alias(db, user_id: str) -> str | None:
    if not user_id:
        return None
    user = await db.get(User, str(user_id))
    if user is not None:
        return user.alias
    return None


async def get_or_create_user_id(db, alias: str, ip: str | None) -> str | None:
    if not alias:
        return None
    user_id = await resolve_user_id(db, alias)
    if user_id is not None:
        return user_id
    import uuid as _uuid
    user = User(id=str(_uuid.uuid4()), username=alias, alias=alias, ip_address=ip)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return str(user.id)
