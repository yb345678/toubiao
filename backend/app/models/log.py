from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin


class Log(IdMixin, Base):
    __tablename__ = "logs"

    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    project_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    analysis_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), index=True)
    level: Mapped[str] = mapped_column(String(50), default="info", index=True)
    module: Mapped[str | None] = mapped_column(String(100), index=True)
    event: Mapped[str | None] = mapped_column(String(100), index=True)
    message: Mapped[str] = mapped_column(Text)
    stack_trace: Mapped[str | None] = mapped_column(Text)
    request_id: Mapped[str | None] = mapped_column(String(100), index=True)
    ip_address: Mapped[str | None] = mapped_column(String(100))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[object] = mapped_column(DateTime, index=True)
    metadata_json: Mapped[str | None] = mapped_column(Text)
