from __future__ import annotations

from pydantic import BaseModel


class ProjectFileRead(BaseModel):
    file_type: str
    original_name: str | None = None
    stored_path: str
    size: int
    content_type: str | None = None


class ProjectFileList(BaseModel):
    items: list[ProjectFileRead]
