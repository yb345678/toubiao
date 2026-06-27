from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProposalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    analysis_id: str
    title: str
    business_outline_json: str | None
    technical_outline_json: str | None
    matched_materials_json: str | None
    markdown_content: str | None
    file_path: str | None
    version: int
    status: str
    created_at: datetime
