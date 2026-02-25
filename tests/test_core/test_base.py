import pytest
from datetime import datetime, timezone
from blog_chat.core.base import Base


class TestBase:
    def test_now_returns_utc_datetime(self):
        result = Base.now()
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc

    def test_now_returns_current_time(self):
        before = datetime.now(timezone.utc)
        result = Base.now()
        after = datetime.now(timezone.utc)
        assert before <= result <= after
