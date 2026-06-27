from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Proposal(IdMixin, TimestampMixin, Base):
    __tablename__ = "proposals"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    analysis_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    business_outline_json: Mapped[str | None] = mapped_column(Text)
    technical_outline_json: Mapped[str | None] = mapped_column(Text)
    matched_materials_json: Mapped[str | None] = mapped_column(Text)
    markdown_content: Mapped[str | None] = mapped_column(Text)
    file_path: Mapped[str | None] = mapped_column(String(1000))
    version: Mapped[int] = mapped_column(Integer, default=1, index=True)
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True)
    metadata_json: Mapped[str | None] = mapped_column(Text)

    project = relationship("Project", back_populates="proposals")
    analysis = relationship("Analysis", back_populates="proposals")
