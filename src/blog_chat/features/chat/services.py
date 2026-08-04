from sqlalchemy import select

from blog_chat.features.accounts.models import User


async def resolve_user_id(db, username: str) -> int | None:
    if not username:
        return None
    user = (await db.execute(
        select(User).where(User.username == username)
    )).scalar_one_or_none()
    return user.id if user is not None else None


async def get_or_create_user_id(db, username: str, ip: str | None) -> int | None:
    if not username:
        return None
    user_id = await resolve_user_id(db, username)
    if user_id is not None:
        return user_id
    user = User(username=username, ip_address=ip)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user.id
