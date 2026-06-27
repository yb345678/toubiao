"""Skill4: bid proposal writer agent."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from app.agents.skills.proposal_writer.schema import ProposalWriterInput, ProposalWriterOutput


BUSINESS_OUTLINE = [
    "Bid letter and legal representative authorization",
    "Enterprise profile and business license",
    "Similar project performance",
    "Project team credentials",
    "Bid deposit proof",
    "Business deviation table and service commitments",
]

TECHNICAL_OUTLINE = [
    "Project understanding and service objectives",
    "Operation and maintenance organization structure",
    "7x24 response and emergency handling mechanism",
    "Quality assurance, SLA, and acceptance method",
    "Security management and data confidentiality",
    "Implementation plan, milestones, and risk control",
]


def _load_materials(path: str, limit: int = 12) -> list[str]:
    qpath = Path(path)
    if not qpath.exists():
        return []

    rows: list[dict[str, Any]]
    if qpath.suffix.lower() in {".xlsx", ".xls"}:
        import pandas as pd

        rows = pd.read_excel(qpath).fillna("").to_dict("records")
    elif qpath.suffix.lower() == ".csv":
        with qpath.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    else:
        rows = []

    materials: list[str] = []
    for row in rows[:limit]:
        name = row.get("name") or row.get("名称") or row.get("title") or next(iter(row.values()), "")
        description = row.get("description") or row.get("描述") or ""
        materials.append(f"{name}: {description}".strip(": "))
    return materials


def _key_info(parsed_document: dict) -> dict:
    info = parsed_document.get("key_info", {})
    return {
        "project_name": info.get("project_name") or info.get("项目名称") or "Tender Project",
        "budget": info.get("budget") or info.get("项目预算") or "Unknown",
        "deadline": info.get("deadline") or info.get("截标时间") or "Unknown",
        "deposit": info.get("deposit") or info.get("保证金") or "Unknown",
        "scoring_weights": info.get("scoring_weights") or info.get("评分权重") or "Unknown",
    }


def _risk_summary(risk_result: dict) -> str:
    summary = risk_result.get("summary", {})
    return f"high={summary.get('high', 0)}, medium={summary.get('medium', 0)}, low={summary.get('low', 0)}"


def write_proposal(payload: ProposalWriterInput) -> ProposalWriterOutput:
    info = _key_info(payload.parsed_document)
    materials = _load_materials(payload.qualification_file_path)
    score = payload.qualification_result.get("score", 0)
    overall_status = payload.qualification_result.get("overall_status", "unknown")
    missing = payload.qualification_result.get("missing_materials", [])
    risk_text = _risk_summary(payload.risk_result)

    material_block = "\n".join(f"- {item}" for item in materials) or "- No matched enterprise materials found."
    missing_block = "\n".join(f"- {item}" for item in missing) or "- No missing material detected."
    risk_block = "\n".join(
        f"- [{risk.get('level')}] Page {risk.get('source_page')}: {risk.get('title')} - {risk.get('mitigation')}"
        for risk in payload.risk_result.get("risks", [])[:6]
    ) or "- No major risk detected by current rules."

    markdown = f"""# Bid Proposal Draft

## 1. Project Overview

- Project name: {info["project_name"]}
- Budget: {info["budget"]}
- Deadline: {info["deadline"]}
- Bid deposit: {info["deposit"]}
- Scoring weights: {info["scoring_weights"]}

## 2. Qualification Summary

- Qualification score: {score}
- Overall status: {overall_status}
- Risk summary: {risk_text}

### Matched Enterprise Materials

{material_block}

### Missing Materials

{missing_block}

## 3. Business Proposal Outline

{chr(10).join(f"- {item}" for item in BUSINESS_OUTLINE)}

## 4. Technical Proposal Outline

{chr(10).join(f"- {item}" for item in TECHNICAL_OUTLINE)}

## 5. Risk Response Plan

{risk_block}

## 6. Submission Recommendation

The project is recommended for bidding if all hard materials are confirmed before submission. The final bid package should be reviewed by business, legal, and project delivery teams.
"""

    return ProposalWriterOutput(
        business_outline=BUSINESS_OUTLINE,
        technical_outline=TECHNICAL_OUTLINE,
        matched_materials=materials,
        markdown_draft=markdown.strip(),
    )


def run(parsed_document: dict, qualification_result: dict, risk_result: dict, qualification_file_path: str) -> dict:
    return write_proposal(
        ProposalWriterInput(
            parsed_document=parsed_document,
            qualification_result=qualification_result,
            risk_result=risk_result,
            qualification_file_path=qualification_file_path,
        )
    ).model_dump()
