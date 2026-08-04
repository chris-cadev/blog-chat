from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from blog_chat.core.base import Base
from blog_chat.features.accounts.models import User
from blog_chat.features.chat.models import Message
from blog_chat.features.chat.routes import get_username_color, load_history
from blog_chat.features.chat.websocket import ConnectionManager, SlidingWindowLimiter


class TestSlidingWindowLimiter:
    def test_allows_within_limit(self):
        limiter = SlidingWindowLimiter(max_events=2, window_seconds=10)
        assert limiter.allow("ip1") is True
        assert limiter.allow("ip1") is True

    def test_rejects_above_limit(self):
        limiter = SlidingWindowLimiter(max_events=2, window_seconds=10)
        assert limiter.allow("ip1") is True
        assert limiter.allow("ip1") is True
        assert limiter.allow("ip1") is False

    def test_keys_are_isolated(self):
        limiter = SlidingWindowLimiter(max_events=1, window_seconds=10)
        assert limiter.allow("ip1") is True
        assert limiter.allow("ip2") is True
        assert limiter.allow("ip1") is False

    def test_window_expiry(self):
        limiter = SlidingWindowLimiter(max_events=1, window_seconds=0.1)
        assert limiter.allow("ip1") is True
        assert limiter.allow("ip1") is False
        limiter._events["ip1"].clear()
        assert limiter.allow("ip1") is True


class FakeWebSocket:
    def __init__(self, host="1.2.3.4"):
        self.host = host
        self.accepted = False
        self.sent = []

    @property
    def client(self):
        return self

    async def accept(self):
        self.accepted = True

    async def send_json(self, data):
        self.sent.append(data)

    async def close(self, code=1000):
        self.closed_code = code


class TestUsernameColor:
    def test_deterministic(self):
        assert get_username_color("Alice") == get_username_color("Alice")

    def test_different_names_get_different_colors(self):
        assert get_username_color("Alice") != get_username_color("Bob")

    def test_returns_hsl_string(self):
        import re

        assert re.match(r"^hsl\(\d+, 70%, 45%\)$", get_username_color("Alice"))

    def test_matches_expected_fnv1a_value(self):
        assert get_username_color("Alice") == "hsl(143, 70%, 45%)"


class TestConnectionManager:
    def test_connect_and_disconnect(self):
        manager = ConnectionManager()
        ws = FakeWebSocket()
        result = await_test(manager.connect(ws, "room1", "Alice", "UTC"))
        assert result is True
        assert ws.accepted is True
        assert ws in manager.active_connections["room1"]
        manager.disconnect(ws, "room1")
        assert "room1" not in manager.active_connections

    def test_disconnect_prunes_empty_room(self):
        manager = ConnectionManager()
        ws = FakeWebSocket()
        await_test(manager.connect(ws, "room1"))
        manager.disconnect(ws, "room1")
        assert "room1" not in manager.active_connections

    def test_per_ip_connection_cap(self):
        manager = ConnectionManager()
        for _ in range(manager.MAX_CONNECTIONS_PER_IP):
            assert await_test(manager.connect(FakeWebSocket(), "room1")) is True
        blocked = FakeWebSocket()
        assert await_test(manager.connect(blocked, "room1")) is False
        assert blocked.closed_code == 1013

    def test_per_room_cap(self):
        manager = ConnectionManager()
        manager.MAX_CONNECTIONS_PER_ROOM = 2
        assert await_test(manager.connect(FakeWebSocket("10.0.0.1"), "room1")) is True
        assert await_test(manager.connect(FakeWebSocket("10.0.0.2"), "room1")) is True
        blocked = FakeWebSocket("10.0.0.3")
        assert await_test(manager.connect(blocked, "room1")) is False

    def test_rate_limited_counts_sends(self):
        manager = ConnectionManager()
        ws = FakeWebSocket()
        await_test(manager.connect(ws, "room1"))
        for _ in range(manager._limiter.max_events):
            assert manager.rate_limited(ws) is False
        assert manager.rate_limited(ws) is True

    def test_broadcast_refresh_sends_to_all_rooms(self):
        manager = ConnectionManager()
        ws1 = FakeWebSocket("10.0.0.1")
        ws2 = FakeWebSocket("10.0.0.2")
        await_test(manager.connect(ws1, "room1"))
        await_test(manager.connect(ws2, "room2"))

        await_test(manager.broadcast_refresh())

        assert [m["type"] for m in ws1.sent] == ["refresh"]
        assert [m["type"] for m in ws2.sent] == ["refresh"]
        assert ws1.sent[0]["reason"] == "database_changed"

    def test_broadcast_refresh_disconnects_failed_socket(self):
        manager = ConnectionManager()
        ws = FakeWebSocket()
        await_test(manager.connect(ws, "room1"))
        ws.send_json = None
        await_test(manager.broadcast_refresh())
        assert "room1" not in manager.active_connections


def await_test(awaitable):
    import asyncio

    return asyncio.run(awaitable)


class TestLoadHistory:
    async def _make_db(self, count):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        maker = async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        now = datetime.now()
        async with maker() as db:
            for i in range(count):
                db.add(Message(
                    room_slug="offtopic",
                    username="Alice",
                    content=f"msg-{i}",
                    timestamp=now + timedelta(seconds=i),
                ))
            await db.commit()
        return maker

    def test_history_newest_first(self):
        async def run():
            maker = await self._make_db(5)
            async with maker() as db:
                messages = await load_history(db, "offtopic", "Alice", None)
            return messages

        messages = await_test(run())
        assert "msg-4" in messages[0]["html"]
        assert "msg-0" in messages[-1]["html"]
        timestamps = [datetime.fromisoformat(m["timestamp"]) for m in messages]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_history_limits_to_50_most_recent(self):
        async def run():
            maker = await self._make_db(55)
            async with maker() as db:
                messages = await load_history(db, "offtopic", "Alice", None)
            return messages

        messages = await_test(run())
        assert len(messages) == 50
        assert "msg-54" in messages[0]["html"]
        assert "msg-5" in messages[-1]["html"]
