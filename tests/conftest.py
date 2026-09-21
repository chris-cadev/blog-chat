import threading
import time

import pytest
import uvicorn

from blog_chat.app import app

PORT = 8199


@pytest.fixture(scope="session", autouse=True)
def live_server():
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1)
    yield f"http://127.0.0.1:{PORT}"
    server.should_exit = True
    thread.join(timeout=5)
