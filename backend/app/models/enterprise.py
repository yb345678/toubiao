from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Enterprise(IdMixin, TimestampMixin, Base):
    __tablename__ = "enterprises"

    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    credit_code: Mapped[str | None] = mapped_column(String(100), index=True)
    industry: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(String(500))
    contact_name: Mapped[str | None] = mapped_column(String(100))
    contact_phone: Mapped[str | None] = mapped_column(String(50))
    contact_email: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="active", index=True)
    deleted_at: Mapped[object | None] = mapped_column(DateTime)
    metadata_json: Mapped[str | None] = mapped_column(Text)

    owner = relationship("User", back_populates="enterprises")
    projects = relationship("Project", back_populates="enterprise")
    qualifications = relationship("Qualification", back_populates="enterprise")
