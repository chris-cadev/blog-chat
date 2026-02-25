from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

CONTENT_DIR = Path("content")
if not CONTENT_DIR.exists():
    raise ValueError(f"Content directory {CONTENT_DIR} does not exist")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///chat.db")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")
if not DATABASE_URL.startswith("sqlite+aiosqlite://") and not DATABASE_URL.startswith("postgresql+asyncpg://"):
    raise ValueError(
        "DATABASE_URL must compatible with either SQLite or PostgreSQL (e.g., sqlite+aiosqlite:///chat.db or postgresql+asyncpg://user:password@localhost/dbname)"
    )

JWT_ALGORITHM = "HS256"
JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is required")
