from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    enterprise_id: str
    name: str
    tender_name: str | None = None
    tender_company: str | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    enterprise_id: str
    created_by: str
    name: str
    tender_name: str | None
    tender_company: str | None
    status: str
    latest_score: int | None
    latest_recommendation: str | None
    created_at: datetime
