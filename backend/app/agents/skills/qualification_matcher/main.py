"""Skill2: qualification matching and scoring agent."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from app.agents.skills.qualification_matcher.schema import (
    QualificationMatcherInput,
    QualificationMatcherOutput,
    RequirementCheck,
)
from app.core.exceptions import ExcelReadError


DEFAULT_REQUIREMENTS = [
    {
        "requirement": "Business license",
        "category": "certificate",
        "hard_requirement": True,
        "keywords": ["营业执照", "business license"],
    },
    {
        "requirement": "Bid deposit proof",
        "category": "material",
        "hard_requirement": True,
        "keywords": ["保证金", "deposit"],
    },
    {
        "requirement": "Project manager certificate",
        "category": "staff",
        "hard_requirement": True,
        "keywords": ["PMP", "信息系统项目管理师", "project manager"],
    },
    {
        "requirement": "Two similar project cases",
        "category": "project_case",
        "hard_requirement": False,
        "keywords": ["智慧园区", "运维", "similar project", "case"],
    },
    {
        "requirement": "Team size no less than eight",
        "category": "staff",
        "hard_requirement": False,
        "keywords": ["8人", "8 人", "团队8", "team 8"],
    },
]


def _load_rows(path: Path) -> list[dict[str, Any]]:
    try:
        if not path.exists():
            raise ExcelReadError(f"Qualification file not found: {path}")
        if path.suffix.lower() in {".xlsx", ".xls"}:
            import pandas as pd

            return pd.read_excel(path).fillna("").to_dict("records")
        if path.suffix.lower() == ".csv":
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                return list(csv.DictReader(handle))
    except ExcelReadError:
        raise
    except Exception as exc:
        raise ExcelReadError(f"Excel qualification ledger read failed: {exc}") from exc
    raise ExcelReadError(f"Unsupported qualification ledger format: {path.suffix}")


def _ledger_text(rows: list[dict[str, Any]]) -> str:
    return "\n".join(" ".join(str(value) for value in row.values()) for row in rows)


def _extract_dynamic_requirements(parsed_document: dict) -> list[dict[str, Any]]:
    """Reserved hook for requirement extraction from Skill1 output.

    The MVP uses default enterprise bidding requirements while keeping this hook
    for future NLP/LLM-based requirement extraction.
    """

    return list(DEFAULT_REQUIREMENTS)


def match_qualifications(payload: QualificationMatcherInput) -> QualificationMatcherOutput:
    path = Path(payload.qualification_file_path)
    rows = _load_rows(path)
    text = _ledger_text(rows)
    requirements = _extract_dynamic_requirements(payload.parsed_document)

    checks: list[RequirementCheck] = []
    missing: list[str] = []
    hard_failed = False

    for item in requirements:
        matched = any(keyword.lower() in text.lower() for keyword in item["keywords"])
        if not matched:
            missing.append(item["requirement"])
            if item["hard_requirement"]:
                hard_failed = True
        checks.append(
            RequirementCheck(
                requirement=item["requirement"],
                category=item["category"],
                hard_requirement=item["hard_requirement"],
                status="matched" if matched else ("hard_failed" if item["hard_requirement"] else "missing"),
                evidence="Matched enterprise qualification ledger keywords." if matched else "No matching material found.",
            )
        )

    matched_count = sum(1 for item in checks if item.status == "matched")
    score = round(matched_count / len(checks) * 100) if checks else 0
    if hard_failed:
        score = min(score, 59)
        overall_status = "hard_failed"
    elif missing:
        overall_status = "missing_materials"
    else:
        overall_status = "qualified"

    bonus_tips = []
    parsed_key_info = payload.parsed_document.get("key_info", {}) if payload.parsed_document else {}
    scoring = str(parsed_key_info.get("scoring_weights") or parsed_key_info.get("评分权重") or "")
    if "技术" in scoring or "technical" in scoring.lower():
        bonus_tips.append("Strengthen SLA, emergency response, quality assurance, and project team resumes.")
    if "商务" in scoring or "business" in scoring.lower():
        bonus_tips.append("Attach similar contracts, acceptance reports, and client references.")
    if score < 90:
        bonus_tips.append("Complete all hard materials first, then improve evidence for scoring items.")

    return QualificationMatcherOutput(
        score=score,
        overall_status=overall_status,
        checks=checks,
        missing_materials=missing,
        bonus_tips=bonus_tips,
        ledger_rows=len(rows),
    )


def run(parsed_document: dict, qualification_file_path: str) -> dict:
    return match_qualifications(
        QualificationMatcherInput(parsed_document=parsed_document, qualification_file_path=qualification_file_path)
    ).model_dump()
