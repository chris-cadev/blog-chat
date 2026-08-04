import asyncio
from pathlib import Path
from typing import Awaitable, Callable

from sqlalchemy.engine import make_url

from blog_chat.core.config import DATABASE_URL

POLL_INTERVAL = 1.0


def sqlite_db_path() -> Path | None:
    if not DATABASE_URL.startswith("sqlite+aiosqlite://"):
        return None
    url = make_url(DATABASE_URL)
    path = url.database
    if not path or path == ":memory:":
        return None
    return Path(path).resolve()


def _signature(path: Path) -> tuple:
    try:
        st = path.stat()
        return (st.st_ino, st.st_mtime_ns, st.st_size)
    except OSError:
        return None


class DatabaseChangeWatcher:
    def __init__(
        self,
        on_change: Callable[[], Awaitable[None]],
        poll_interval: float = POLL_INTERVAL,
    ):
        self._on_change = on_change
        self._poll_interval = poll_interval
        self._task: asyncio.Task | None = None
        self._baseline: tuple | None = None

    @property
    def enabled(self) -> bool:
        return sqlite_db_path() is not None

    def start(self):
        if self._task is not None or not self.enabled:
            return
        self._baseline = _signature(sqlite_db_path())
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None

    def note_internal_change(self, path: Path | None = None):
        path = path or sqlite_db_path()
        if path is None:
            return
        self._baseline = _signature(path)

    async def _run(self, path: Path | None = None):
        path = path or sqlite_db_path()
        if path is None:
            return
        while True:
            await asyncio.sleep(self._poll_interval)
            sig = _signature(path)
            if sig != self._baseline:
                self._baseline = sig
                try:
                    await self._on_change()
                except Exception:
                    pass
