from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Project(IdMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    enterprise_id: Mapped[str] = mapped_column(String(36), ForeignKey("enterprises.id", ondelete="CASCADE"), index=True)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tender_name: Mapped[str | None] = mapped_column(String(255))
    tender_company: Mapped[str | None] = mapped_column(String(255))
    tender_budget: Mapped[str | None] = mapped_column(String(100))
    tender_deadline: Mapped[object | None] = mapped_column(DateTime)
    tender_pdf_path: Mapped[str | None] = mapped_column(String(1000))
    qualification_file_path: Mapped[str | None] = mapped_column(String(1000))
    tender_file_url: Mapped[str | None] = mapped_column(String(2000))
    tender_file_name: Mapped[str | None] = mapped_column(String(500))
    tender_file_size: Mapped[int | None] = mapped_column(Integer)
    tender_file_content_type: Mapped[str | None] = mapped_column(String(255))
    qualification_file_url: Mapped[str | None] = mapped_column(String(2000))
    qualification_file_name: Mapped[str | None] = mapped_column(String(500))
    qualification_file_size: Mapped[int | None] = mapped_column(Integer)
    qualification_file_content_type: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="created", index=True)
    latest_score: Mapped[int | None] = mapped_column(Integer)
    latest_recommendation: Mapped[str | None] = mapped_column(String(100))
    latest_analysis_id: Mapped[str | None] = mapped_column(String(36), index=True)
    deleted_at: Mapped[object | None] = mapped_column(DateTime)
    metadata_json: Mapped[str | None] = mapped_column(Text)

    enterprise = relationship("Enterprise", back_populates="projects")
    creator = relationship("User", back_populates="projects")
    analyses = relationship("Analysis", back_populates="project")
    risks = relationship("Risk", back_populates="project")
    proposals = relationship("Proposal", back_populates="project")

    @property
    def files_ready(self) -> bool:
        return bool(self.tender_file_url and self.qualification_file_url)
