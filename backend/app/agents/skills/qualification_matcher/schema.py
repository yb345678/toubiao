from __future__ import annotations

from pydantic import BaseModel, Field


class RequirementCheck(BaseModel):
    requirement: str
    category: str
    hard_requirement: bool
    status: str
    evidence: str | None = None


class QualificationMatcherInput(BaseModel):
    parsed_document: dict
    qualification_file_path: str


class QualificationMatcherOutput(BaseModel):
    agent: str = "qualification_matcher"
    status: str = "success"
    score: int
    overall_status: str
    checks: list[RequirementCheck]
    missing_materials: list[str] = Field(default_factory=list)
    bonus_tips: list[str] = Field(default_factory=list)
    ledger_rows: int = 0
