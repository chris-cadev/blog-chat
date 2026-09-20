import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from blog_chat.core.base import Base
from blog_chat.features.accounts.models import User
from blog_chat.features.accounts.services import assign_username, generate_guest_name


class TestGenerateGuestName:
    def test_format(self):
        name = generate_guest_name()
        assert re.fullmatch(r"[A-Z][a-z]+[A-Z][a-z]+-\d{4}", name)

    def test_uniqueness(self):
        names = {generate_guest_name() for _ in range(100)}
        assert len(names) == 100


class TestAssignUsername:
    async def _make_db(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        maker = async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return maker

    def test_rename_reuses_user_row(self):
        async def run():
            maker = await self._make_db()
            async with maker() as db:
                user = User(username="Alice", ip_address="1.2.3.4")
                db.add(user)
                await db.commit()
                await db.refresh(user)
                original_id = user.id

                await assign_username(db, "Carol", "Alice", "1.2.3.4")

                row = (await db.execute(
                    select(User).where(User.id == original_id)
                )).scalar_one_or_none()
                return original_id, row.username, row.alias, row.id

        original_id, username, alias, row_id = asyncio_run(run())
        assert username == "Alice"
        assert alias == "Carol"
        assert row_id == original_id

    def test_new_username_creates_row(self):
        async def run():
            maker = await self._make_db()
            async with maker() as db:
                await assign_username(db, "Carol", None, "1.2.3.4")
            async with maker() as db:
                rows = (await db.execute(select(User))).scalars().all()
            return [(r.username, r.ip_address) for r in rows]

        rows = asyncio_run(run())
        assert rows == [("Carol", "1.2.3.4")]


def asyncio_run(awaitable):
    import asyncio

    return asyncio.run(awaitable)
