from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Analysis(IdMixin, TimestampMixin, Base):
    __tablename__ = "analyses"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    started_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    current_step: Mapped[str | None] = mapped_column(String(100))
    score: Mapped[int | None] = mapped_column(Integer, index=True)
    recommendation: Mapped[str | None] = mapped_column(String(100))
    summary: Mapped[str | None] = mapped_column(Text)
    parsed_document_json: Mapped[str | None] = mapped_column(Text)
    qualification_result_json: Mapped[str | None] = mapped_column(Text)
    risk_result_json: Mapped[str | None] = mapped_column(Text)
    proposal_result_json: Mapped[str | None] = mapped_column(Text)
    final_report_json: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[object | None] = mapped_column(DateTime)
    finished_at: Mapped[object | None] = mapped_column(DateTime)
    metadata_json: Mapped[str | None] = mapped_column(Text)

    project = relationship("Project", back_populates="analyses")
    risks = relationship("Risk", back_populates="analysis")
    proposals = relationship("Proposal", back_populates="analysis")
