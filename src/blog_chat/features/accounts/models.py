from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import uuid

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from blog_chat.core.base import Base

if TYPE_CHECKING:
    from blog_chat.features.chat.models import Message


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(50), unique=True)
    alias: Mapped[str] = mapped_column(String(50), unique=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=Base.now)

    messages: Mapped[list["Message"]] = relationship(back_populates="user")

    def __init__(self, **kwargs):
        if "alias" not in kwargs and "username" in kwargs:
            kwargs["alias"] = kwargs["username"]
        super().__init__(**kwargs)
