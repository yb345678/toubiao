"""Database initialization helpers."""

from __future__ import annotations

from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
from pathlib import Path
from sqlalchemy import inspect, text


PROJECT_EXTRA_COLUMNS = {
    "tender_file_url": "VARCHAR(2000)",
    "tender_file_name": "VARCHAR(500)",
    "tender_file_size": "INTEGER",
    "tender_file_content_type": "VARCHAR(255)",
    "qualification_file_url": "VARCHAR(2000)",
    "qualification_file_name": "VARCHAR(500)",
    "qualification_file_size": "INTEGER",
    "qualification_file_content_type": "VARCHAR(255)",
}


def _quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def ensure_project_file_columns() -> None:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "projects" not in table_names:
        return
    existing = {column["name"] for column in inspector.get_columns("projects")}
    missing = [(name, column_type) for name, column_type in PROJECT_EXTRA_COLUMNS.items() if name not in existing]
    if not missing:
        return
    with engine.begin() as connection:
        for name, column_type in missing:
            connection.execute(text(f"ALTER TABLE projects ADD COLUMN {_quote_identifier(name)} {column_type}"))


def init_db() -> None:
    import app.models  # noqa: F401

    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    ensure_project_file_columns()
