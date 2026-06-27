"""Multi-agent workflow Router.

The Router is responsible for orchestration only:

- create shared context
- call each independent Skill Agent
- collect status records
- normalize final decision fields
- build a report payload for persistence and frontend rendering

Agent business logic stays outside this file.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from app.agents.protocol import AgentContext, AgentRunRecord, ProgressCallback, utc_now_iso
from app.core.exceptions import AgentExecutionError, AppError

WORKFLOW_STEPS = [
    {
        "order": 1,
        "key": "pdf_parser",
        "name": "Skill1 PDF Parser Agent",
        "input": ["tender_pdf_path"],
        "output": ["parsed_document"],
    },
    {
        "order": 2,
        "key": "qualification_matcher",
        "name": "Skill2 Qualification Matcher Agent",
        "input": ["parsed_document", "qualification_file_path"],
        "output": ["qualification_result"],
    },
    {
        "order": 3,
        "key": "risk_reviewer",
        "name": "Skill3 Risk Reviewer Agent",
        "input": ["parsed_document"],
        "output": ["risk_result"],
    },
    {
        "order": 4,
        "key": "proposal_writer",
        "name": "Skill4 Proposal Writer Agent",
        "input": ["parsed_document", "qualification_result", "risk_result", "qualification_file_path"],
        "output": ["proposal_result"],
    },
]


def _ensure_repo_root() -> None:
    root = Path(__file__).resolve().parents[4]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


class WorkflowRouter:
    """Sequential multi-agent router for the bidding workflow."""

    def __init__(self, progress_callback: ProgressCallback | None = None):
        self.progress_callback = progress_callback
        self.agent_runs: list[AgentRunRecord] = []

    def _emit(self, step: str, progress: int) -> None:
        if self.progress_callback:
            self.progress_callback(step, progress)

    def _record_success(self, agent_name: str, started_at: str, output: dict, input_summary: dict | None = None) -> None:
        self.agent_runs.append(
            AgentRunRecord(
                agent_name=agent_name,
                status="completed",
                started_at=started_at,
                finished_at=utc_now_iso(),
                input_summary=input_summary or {},
                output_summary=self._summarize_output(output),
            )
        )

    def _record_failed(self, agent_name: str, started_at: str, exc: Exception) -> None:
        self.agent_runs.append(
            AgentRunRecord(
                agent_name=agent_name,
                status="failed",
                started_at=started_at,
                finished_at=utc_now_iso(),
                error_message=str(exc),
            )
        )

    @staticmethod
    def _summarize_output(output: dict) -> dict:
        return {
            "status": output.get("status"),
            "score": output.get("score"),
            "page_count": output.get("page_count"),
            "risk_count": len(output.get("risks", [])) if isinstance(output.get("risks"), list) else None,
        }

    @staticmethod
    def _high_risk_count(risk_result: dict) -> int:
        summary = risk_result.get("summary", {})
        return int(summary.get("high", summary.get("高风险", 0)) or 0)

    @staticmethod
    def _recommendation(score: int, high_risk_count: int, qualification_status: str) -> str:
        if "hard" in qualification_status.lower() or "硬性" in qualification_status:
            return "no_bid"
        if high_risk_count >= 2:
            return "cautious"
        if score >= 80:
            return "bid"
        return "cautious"

    def run(self, tender_pdf_path: str, qualification_file_path: str) -> dict:
        _ensure_repo_root()
        from app.agents.skills.pdf_parser.main import run as parse_pdf
        from app.agents.skills.qualification_matcher.main import run as match_qualification
        from app.agents.skills.risk_reviewer.main import run as review_risk
        from app.agents.skills.proposal_writer.main import run as write_proposal

        context = AgentContext(tender_pdf_path=tender_pdf_path, qualification_file_path=qualification_file_path)

        self._emit("pdf_parser", 10)
        started = utc_now_iso()
        try:
            context.parsed_document = parse_pdf(context.tender_pdf_path)
            self._record_success("pdf_parser", started, context.parsed_document, {"file": tender_pdf_path})
            self._emit("pdf_parser_completed", 30)
        except Exception as exc:
            self._record_failed("pdf_parser", started, exc)
            if isinstance(exc, AppError):
                raise
            raise AgentExecutionError(f"pdf_parser failed: {exc}") from exc

        self._emit("qualification_matcher", 35)
        started = utc_now_iso()
        try:
            context.qualification_result = match_qualification(context.parsed_document, context.qualification_file_path)
            self._record_success("qualification_matcher", started, context.qualification_result, {"file": qualification_file_path})
            self._emit("qualification_matcher_completed", 55)
        except Exception as exc:
            self._record_failed("qualification_matcher", started, exc)
            if isinstance(exc, AppError):
                raise
            raise AgentExecutionError(f"qualification_matcher failed: {exc}") from exc

        self._emit("risk_reviewer", 60)
        started = utc_now_iso()
        try:
            context.risk_result = review_risk(context.parsed_document)
            context.risk_result = self._normalize_risk_result(context.risk_result)
            self._record_success("risk_reviewer", started, context.risk_result)
            self._emit("risk_reviewer_completed", 75)
        except Exception as exc:
            self._record_failed("risk_reviewer", started, exc)
            if isinstance(exc, AppError):
                raise
            raise AgentExecutionError(f"risk_reviewer failed: {exc}") from exc

        self._emit("proposal_writer", 80)
        started = utc_now_iso()
        try:
            context.proposal_result = write_proposal(
                context.parsed_document,
                context.qualification_result,
                context.risk_result,
                context.qualification_file_path,
            )
            self._record_success("proposal_writer", started, context.proposal_result)
            self._emit("proposal_writer_completed", 90)
        except Exception as exc:
            self._record_failed("proposal_writer", started, exc)
            if isinstance(exc, AppError):
                raise
            raise AgentExecutionError(f"proposal_writer failed: {exc}") from exc

        self._emit("report_building", 95)
        return self._build_report(context)

    def _normalize_risk_result(self, risk_result: dict) -> dict:
        summary = risk_result.get("summary", {})
        normalized_summary = {
            "high": int(summary.get("high", summary.get("高风险", 0)) or 0),
            "medium": int(summary.get("medium", summary.get("中风险", 0)) or 0),
            "low": int(summary.get("low", summary.get("低风险", 0)) or 0),
        }
        risk_result["summary"] = normalized_summary
        return risk_result

    def _build_report(self, context: AgentContext) -> dict:
        qualification = context.qualification_result or {}
        risk = context.risk_result or {}
        score = int(qualification.get("score", 0) or 0)
        qualification_status = qualification.get("overall_status", "")
        high_risk_count = self._high_risk_count(risk)
        recommendation = self._recommendation(score, high_risk_count, qualification_status)

        return {
            "workflow": "pdf_parse -> qualification_match -> risk_review -> proposal_write -> report",
            "workflow_steps": WORKFLOW_STEPS,
            "input_files": {
                "tender_pdf": context.tender_pdf_path,
                "qualification_file": context.qualification_file_path,
            },
            "agent_runs": [record.__dict__ for record in self.agent_runs],
            "agents": {
                "pdf_parser": context.parsed_document,
                "qualification_matcher": context.qualification_result,
                "risk_reviewer": context.risk_result,
                "proposal_writer": context.proposal_result,
            },
            "decision": {
                "recommendation": recommendation,
                "score": score,
                "qualification_status": qualification_status,
                "high_risk_count": high_risk_count,
                "summary": "Multi-agent bidding analysis completed.",
            },
        }


def run_analysis_workflow(
    tender_pdf_path: str,
    qualification_file_path: str,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    """Compatibility wrapper used by the analysis service."""

    return WorkflowRouter(progress_callback=progress_callback).run(tender_pdf_path, qualification_file_path)
