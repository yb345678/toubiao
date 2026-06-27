from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    status: str
    progress: int
    current_step: str | None
    score: int | None
    recommendation: str | None
    summary: str | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None


class AnalysisStartResponse(BaseModel):
    task_id: str
    status: str
