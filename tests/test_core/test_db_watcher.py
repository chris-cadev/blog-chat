import asyncio
import os
import tempfile
from pathlib import Path

import blog_chat.core.db_watcher as db_watcher_module
from blog_chat.core.db_watcher import DatabaseChangeWatcher, _signature, sqlite_db_path


def await_test(awaitable):
    return asyncio.run(awaitable)


class TestSqliteDbPath:
    def test_relative_url_resolves_to_relative_file(self, monkeypatch):
        monkeypatch.setattr(db_watcher_module, "DATABASE_URL", "sqlite+aiosqlite:///chat.db")
        assert sqlite_db_path() == Path("chat.db").resolve()

    def test_absolute_url_resolves_to_absolute_file(self, monkeypatch):
        monkeypatch.setattr(
            db_watcher_module,
            "DATABASE_URL",
            f"sqlite+aiosqlite:///{Path('/tmp/foo/bar.db').resolve()}",
        )
        assert sqlite_db_path() == Path("/tmp/foo/bar.db").resolve()

    def test_postgres_url_returns_none(self, monkeypatch):
        monkeypatch.setattr(
            db_watcher_module,
            "DATABASE_URL",
            "postgresql+asyncpg://user:pass@localhost/db",
        )
        assert sqlite_db_path() is None

    def test_memory_url_returns_none(self, monkeypatch):
        monkeypatch.setattr(db_watcher_module, "DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        assert sqlite_db_path() is None


class TestSignature:
    def test_missing_file_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            assert _signature(Path(tmp) / "nope.db") is None

    def test_signature_changes_on_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chat.db"
            path.write_bytes(b"data")
            before = _signature(path)
            assert before is not None
            path.write_bytes(b"data2")
            after = _signature(path)
            assert after != before


class TestDatabaseChangeWatcher:
    def test_detects_external_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chat.db"
            path.write_bytes(b"data")
            changed = []

            async def on_change():
                changed.append(True)

            watcher = DatabaseChangeWatcher(on_change=on_change, poll_interval=0.01)
            watcher._baseline = _signature(path)

            async def drive():
                watcher._task = asyncio.ensure_future(watcher._run(path))
                path.write_bytes(b"changed!")
                for _ in range(100):
                    await asyncio.sleep(0.01)
                    if changed:
                        break
                watcher._task.cancel()
                try:
                    await watcher._task
                except asyncio.CancelledError:
                    pass

            await_test(drive())
            assert changed == [True]

    def test_note_internal_change_suppresses(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chat.db"
            path.write_bytes(b"data")
            changed = []

            async def on_change():
                changed.append(True)

            watcher = DatabaseChangeWatcher(on_change=on_change, poll_interval=0.01)
            watcher._baseline = _signature(path)
            path.write_bytes(b"internal")
            watcher.note_internal_change(path)

            async def drive():
                watcher._task = asyncio.ensure_future(watcher._run(path))
                for _ in range(50):
                    await asyncio.sleep(0.01)
                watcher._task.cancel()
                try:
                    await watcher._task
                except asyncio.CancelledError:
                    pass

            await_test(drive())
            assert changed == []
