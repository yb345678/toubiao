from __future__ import annotations

from pydantic import BaseModel, Field


class PageText(BaseModel):
    page_number: int
    text: str
    ocr_used: bool = False


class TableData(BaseModel):
    page_number: int
    rows: list[list[str | None]] = Field(default_factory=list)
    text: str = ""


class EvidenceItem(BaseModel):
    field: str
    page_number: int
    keyword: str
    quote: str


class ParsedKeyInfo(BaseModel):
    project_name: str | None = None
    budget: str | None = None
    deadline: str | None = None
    deposit: str | None = None
    qualification_requirements: str | None = None
    rejection_clauses: str | None = None
    scoring_weights: str | None = None


class PDFParserInput(BaseModel):
    pdf_path: str


class PDFParserOutput(BaseModel):
    agent: str = "pdf_parser"
    status: str = "success"
    source_file: str
    page_count: int
    full_text: str
    pages: list[PageText]
    tables: list[TableData]
    key_info: ParsedKeyInfo
    evidence: list[EvidenceItem]
    notes: list[str] = Field(default_factory=list)
