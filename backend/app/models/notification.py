from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin


class Notification(IdMixin, Base):
    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    analysis_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="unread", index=True)
    priority: Mapped[str] = mapped_column(String(50), default="normal", index=True)
    read_at: Mapped[object | None] = mapped_column(DateTime)
    created_at: Mapped[object] = mapped_column(DateTime, index=True)
    metadata_json: Mapped[str | None] = mapped_column(Text)
