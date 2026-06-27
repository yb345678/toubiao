"""Database initialization helpers."""

from __future__ import annotations

from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
from pathlib import Path


def init_db() -> None:
    import app.models  # noqa: F401

    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
