from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Risk(IdMixin, TimestampMixin, Base):
    __tablename__ = "risks"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    analysis_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), index=True)
    level: Mapped[str] = mapped_column(String(50), index=True)
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(255))
    source_page: Mapped[int | None] = mapped_column(Integer)
    original_text: Mapped[str | None] = mapped_column(Text)
    negative_impact: Mapped[str | None] = mapped_column(Text)
    mitigation: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="open", index=True)
    metadata_json: Mapped[str | None] = mapped_column(Text)

    project = relationship("Project", back_populates="risks")
    analysis = relationship("Analysis", back_populates="risks")
