
from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    @staticmethod
    def now():
        return datetime.now(timezone.utc)
