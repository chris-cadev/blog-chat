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
