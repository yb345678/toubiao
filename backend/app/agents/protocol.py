"""Shared Agent protocol and workflow data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Protocol


ProgressCallback = Callable[[str, int], None]


class Agent(Protocol):
    name: str

    def run(self, context: "AgentContext") -> dict:
        ...


@dataclass
class AgentContext:
    tender_pdf_path: str
    qualification_file_path: str
    parsed_document: dict | None = None
    qualification_result: dict | None = None
    risk_result: dict | None = None
    proposal_result: dict | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentRunRecord:
    agent_name: str
    status: str
    started_at: str
    finished_at: str | None = None
    input_summary: Dict[str, Any] = field(default_factory=dict)
    output_summary: Dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"
