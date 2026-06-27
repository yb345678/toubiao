from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EnterpriseCreate(BaseModel):
    name: str
    credit_code: str | None = None
    industry: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    description: str | None = None


class EnterpriseRead(EnterpriseCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_user_id: str
    status: str
    created_at: datetime
