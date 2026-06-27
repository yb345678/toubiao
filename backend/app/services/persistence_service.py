from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.history import History
from app.models.log import Log
from app.models.project import Project
from app.models.proposal import Proposal
from app.models.risk import Risk
from app.models.user import User


def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)


def record_history(
    db: Session,
    *,
    user: User | None,
    project: Project | None = None,
    analysis: Analysis | None = None,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    description: str | None = None,
    before: Any | None = None,
    after: Any | None = None,
    metadata: Any | None = None,
) -> History:
    item = History(
        user_id=user.id if user else None,
        project_id=project.id if project else None,
        analysis_id=analysis.id if analysis else None,
        action=action,
        target_type=target_type,
        target_id=target_id,
        before_json=dump_json(before) if before is not None else None,
        after_json=dump_json(after) if after is not None else None,
        description=description,
        created_at=datetime.utcnow(),
        metadata_json=dump_json(metadata) if metadata is not None else None,
    )
    db.add(item)
    return item


def record_log(
    db: Session,
    *,
    user: User | None,
    project: Project | None = None,
    analysis: Analysis | None = None,
    level: str = "info",
    module: str | None = None,
    event: str | None = None,
    message: str,
    stack_trace: str | None = None,
    metadata: Any | None = None,
) -> Log:
    item = Log(
        user_id=user.id if user else None,
        project_id=project.id if project else None,
        analysis_id=analysis.id if analysis else None,
        level=level,
        module=module,
        event=event,
        message=message,
        stack_trace=stack_trace,
        created_at=datetime.utcnow(),
        metadata_json=dump_json(metadata) if metadata is not None else None,
    )
    db.add(item)
    return item


def persist_risks(db: Session, project: Project, analysis: Analysis, risk_result: dict) -> list[Risk]:
    db.query(Risk).filter(Risk.analysis_id == analysis.id).delete()
    saved: list[Risk] = []
    for item in risk_result.get("risks", []):
        risk = Risk(
            project_id=project.id,
            analysis_id=analysis.id,
            level=str(item.get("level") or "low"),
            category=item.get("category"),
            title=str(item.get("title") or "Untitled risk"),
            source_page=item.get("source_page"),
            original_text=item.get("original_text"),
            negative_impact=item.get("negative_impact"),
            mitigation=item.get("mitigation"),
            status="open",
            metadata_json=dump_json(item),
        )
        db.add(risk)
        saved.append(risk)
    return saved


def persist_proposal(db: Session, project: Project, analysis: Analysis, proposal_result: dict) -> Proposal:
    existing_count = db.query(Proposal).filter(Proposal.project_id == project.id).count()
    proposal = Proposal(
        project_id=project.id,
        analysis_id=analysis.id,
        title=f"{project.name} Bid Proposal",
        business_outline_json=dump_json(proposal_result.get("business_outline", [])),
        technical_outline_json=dump_json(proposal_result.get("technical_outline", [])),
        matched_materials_json=dump_json(proposal_result.get("matched_materials", [])),
        markdown_content=proposal_result.get("markdown_draft"),
        version=existing_count + 1,
        status="draft",
        metadata_json=dump_json({"agent": proposal_result.get("agent"), "status": proposal_result.get("status")}),
    )
    db.add(proposal)
    return proposal
