from __future__ import annotations

from pydantic import BaseModel, Field


class RiskItem(BaseModel):
    level: str
    category: str
    title: str
    source_page: int | None = None
    original_text: str
    negative_impact: str
    mitigation: str


class RiskReviewerInput(BaseModel):
    parsed_document: dict


class RiskReviewerOutput(BaseModel):
    agent: str = "risk_reviewer"
    status: str = "success"
    risks: list[RiskItem] = Field(default_factory=list)
    summary: dict[str, int] = Field(default_factory=lambda: {"high": 0, "medium": 0, "low": 0})
