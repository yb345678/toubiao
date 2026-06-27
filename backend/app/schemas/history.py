from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str | None
    project_id: str | None
    analysis_id: str | None
    action: str
    target_type: str | None
    target_id: str | None
    description: str | None
    created_at: datetime
