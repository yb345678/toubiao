from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RiskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    analysis_id: str
    level: str
    category: str | None
    title: str
    source_page: int | None
    original_text: str | None
    negative_impact: str | None
    mitigation: str | None
    status: str
    created_at: datetime
