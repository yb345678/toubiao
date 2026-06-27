from __future__ import annotations

from pydantic import BaseModel, Field


class ProposalWriterInput(BaseModel):
    parsed_document: dict
    qualification_result: dict
    risk_result: dict
    qualification_file_path: str


class ProposalWriterOutput(BaseModel):
    agent: str = "proposal_writer"
    status: str = "success"
    business_outline: list[str] = Field(default_factory=list)
    technical_outline: list[str] = Field(default_factory=list)
    matched_materials: list[str] = Field(default_factory=list)
    markdown_draft: str
