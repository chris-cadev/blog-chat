
import time
from collections import defaultdict, deque

from fastapi import WebSocket

ConnectionMeta = tuple[str, str | None]


class SlidingWindowLimiter:
    def __init__(self, max_events: int, window_seconds: float):
        self.max_events = max_events
        self.window_seconds = window_seconds
        self._events: dict[str, deque] = {}
        self._prune_threshold = 10_000

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        bucket = self._events.get(key)
        if bucket is None:
            bucket = deque()
            self._events[key] = bucket
        cutoff = now - self.window_seconds
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= self.max_events:
            return False
        bucket.append(now)
        if len(self._events) > self._prune_threshold:
            self._prune()
        return True

    def _prune(self):
        cutoff = time.monotonic() - self.window_seconds
        stale = [k for k, v in self._events.items() if not v or v[-1] <= cutoff]
        for key in stale:
            del self._events[key]


class ConnectionManager:
    MAX_CONNECTIONS_PER_ROOM = 200
    MAX_CONNECTIONS_PER_IP = 5

    def __init__(self):
        self.active_connections: dict[str, dict[WebSocket, ConnectionMeta]] = {}
        self._ip_count: dict[str, int] = defaultdict(int)
        self._limiter = SlidingWindowLimiter(max_events=10, window_seconds=10)

    async def connect(
        self,
        websocket: WebSocket,
        room: str,
        username: str = "Guest",
        timezone: str | None = None,
    ) -> bool:
        await websocket.accept()
        if len(self.active_connections.get(room, ())) >= self.MAX_CONNECTIONS_PER_ROOM:
            await websocket.send_json({
                "type": "error",
                "message": "Room is full. Please try again later.",
            })
            await websocket.close(code=1013)
            return False
        ip = self._ip_key(websocket)
        if self._ip_count[ip] >= self.MAX_CONNECTIONS_PER_IP:
            await websocket.send_json({
                "type": "error",
                "message": "Too many active connections from your IP.",
            })
            await websocket.close(code=1013)
            return False
        self._ip_count[ip] += 1
        room_connections = self.active_connections.setdefault(room, {})
        room_connections[websocket] = (username, timezone)
        return True

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections:
            self.active_connections[room].pop(websocket, None)
            if not self.active_connections[room]:
                del self.active_connections[room]
        ip = self._ip_key(websocket)
        if self._ip_count[ip] > 0:
            self._ip_count[ip] -= 1

    def rate_limited(self, websocket: WebSocket) -> bool:
        return not self._limiter.allow(self._ip_key(websocket))

    async def broadcast(self, room: str, make_payload):
        recipients = list(self.active_connections.get(room, {}).items())
        for connection, meta in recipients:
            try:
                payload = await make_payload(*meta)
                await connection.send_json(payload)
            except Exception:
                self.disconnect(connection, room)

    async def broadcast_refresh(self, reason: str = "database_changed"):
        async def make_refresh_payload(_username: str, _timezone: str | None) -> dict:
            return {"type": "refresh", "reason": reason}

        for room in list(self.active_connections.keys()):
            await self.broadcast(room, make_refresh_payload)

    @staticmethod
    def _ip_key(websocket: WebSocket) -> str:
        return websocket.client.host if websocket.client else "unknown"
