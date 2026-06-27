from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Qualification(IdMixin, TimestampMixin, Base):
    __tablename__ = "qualifications"

    enterprise_id: Mapped[str] = mapped_column(String(36), ForeignKey("enterprises.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    certificate_no: Mapped[str | None] = mapped_column(String(255))
    issuer: Mapped[str | None] = mapped_column(String(255))
    holder_name: Mapped[str | None] = mapped_column(String(255))
    valid_from: Mapped[object | None] = mapped_column(DateTime)
    valid_until: Mapped[object | None] = mapped_column(DateTime, index=True)
    file_path: Mapped[str | None] = mapped_column(String(1000))
    source_file_path: Mapped[str | None] = mapped_column(String(1000))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="valid", index=True)
    deleted_at: Mapped[object | None] = mapped_column(DateTime)
    metadata_json: Mapped[str | None] = mapped_column(Text)

    enterprise = relationship("Enterprise", back_populates="qualifications")
