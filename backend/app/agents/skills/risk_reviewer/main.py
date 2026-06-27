"""Skill3: bid risk reviewer agent."""

from __future__ import annotations

import re
from typing import Iterable

from app.agents.skills.risk_reviewer.schema import RiskItem, RiskReviewerInput, RiskReviewerOutput


RISK_RULES = [
    {
        "level": "high",
        "category": "rejection",
        "title": "Mandatory document rejection risk",
        "keywords": ["废标", "无效投标", "否决投标", "按无效投标处理"],
        "negative_impact": "The bid may be rejected directly if mandatory documents are missing or invalid.",
        "mitigation": "Create a mandatory document checklist and perform business, legal, and project-manager review before submission.",
    },
    {
        "level": "high",
        "category": "qualification",
        "title": "Hard qualification failure risk",
        "keywords": ["必须具备", "须具备", "不满足资格", "资格审查不通过"],
        "negative_impact": "Failure to satisfy hard qualification conditions can block bidding eligibility.",
        "mitigation": "Map each hard requirement to enterprise certificates, staff credentials, and stamped proof materials.",
    },
    {
        "level": "medium",
        "category": "delivery_cost",
        "title": "High service response cost risk",
        "keywords": ["7x24", "驻场", "30分钟", "响应时间", "到场"],
        "negative_impact": "Strict response requirements may increase staffing, duty, and delivery costs.",
        "mitigation": "Estimate response cost in pricing and define escalation paths, service boundaries, and exception handling.",
    },
    {
        "level": "medium",
        "category": "contract_penalty",
        "title": "Penalty and deduction risk",
        "keywords": ["违约金", "扣减", "赔偿", "解除合同", "处罚"],
        "negative_impact": "Penalty clauses may create financial exposure during project delivery.",
        "mitigation": "Clarify penalty caps, acceptance criteria, and force majeure or third-party dependency exceptions.",
    },
    {
        "level": "low",
        "category": "clarification",
        "title": "Clarification or negotiation item",
        "keywords": ["建议", "优先", "可协商", "澄清"],
        "negative_impact": "The item is unlikely to invalidate the bid but may affect later negotiation.",
        "mitigation": "Prepare clarification questions and record acceptable deviations in the bid response.",
    },
]


def _pages(parsed_document: dict) -> list[dict]:
    pages = parsed_document.get("pages", [])
    normalized = []
    for item in pages:
        normalized.append(
            {
                "page_number": item.get("page_number") or item.get("page") or 1,
                "text": item.get("text", ""),
            }
        )
    if not normalized and parsed_document.get("full_text"):
        normalized.append({"page_number": 1, "text": parsed_document["full_text"]})
    return normalized


def _find_hits(pages: list[dict], keywords: Iterable[str], limit: int = 8) -> list[dict]:
    hits: list[dict] = []
    for page in pages:
        text = re.sub(r"\s+", " ", str(page.get("text", "")))
        for keyword in keywords:
            pos = text.find(keyword)
            if pos >= 0:
                left = max(0, pos - 70)
                right = min(len(text), pos + len(keyword) + 110)
                hits.append({"page": int(page.get("page_number", 1)), "quote": text[left:right].strip(), "keyword": keyword})
                break
        if len(hits) >= limit:
            break
    return hits


def review_risks(payload: RiskReviewerInput) -> RiskReviewerOutput:
    pages = _pages(payload.parsed_document)
    risks: list[RiskItem] = []
    seen = set()

    for rule in RISK_RULES:
        for hit in _find_hits(pages, rule["keywords"]):
            key = (rule["level"], rule["category"], hit["page"], hit["quote"])
            if key in seen:
                continue
            seen.add(key)
            risks.append(
                RiskItem(
                    level=rule["level"],
                    category=rule["category"],
                    title=rule["title"],
                    source_page=hit["page"],
                    original_text=hit["quote"],
                    negative_impact=rule["negative_impact"],
                    mitigation=rule["mitigation"],
                )
            )

    if not risks:
        risks.append(
            RiskItem(
                level="low",
                category="manual_review",
                title="Manual legal review still required",
                source_page=1,
                original_text="No high-frequency risk keywords were detected by current rules.",
                negative_impact="Non-standard contractual or formatting risks may still be missed.",
                mitigation="Keep a manual legal review step before formal submission.",
            )
        )

    summary = {"high": 0, "medium": 0, "low": 0}
    for risk in risks:
        summary[risk.level] = summary.get(risk.level, 0) + 1

    return RiskReviewerOutput(risks=risks, summary=summary)


def run(parsed_document: dict) -> dict:
    return review_risks(RiskReviewerInput(parsed_document=parsed_document)).model_dump()
