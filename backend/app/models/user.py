from __future__ import annotations

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    last_login_at: Mapped[object | None] = mapped_column(DateTime)
    deleted_at: Mapped[object | None] = mapped_column(DateTime)
    metadata_json: Mapped[str | None] = mapped_column(Text)

    enterprises = relationship("Enterprise", back_populates="owner")
    projects = relationship("Project", back_populates="creator")
