from __future__ import annotations

from pydantic import BaseModel


class ReportRead(BaseModel):
    analysis_id: str
    project_id: str
    final_report: dict
