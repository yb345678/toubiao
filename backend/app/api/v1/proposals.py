from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import not_found
from app.db.session import get_db
from app.models.proposal import Proposal
from app.models.user import User
from app.schemas.proposal import ProposalRead
from app.services.project_service import get_project_for_user


router = APIRouter()


@router.get("/projects/{project_id}/proposals", response_model=list[ProposalRead])
def list_project_proposals(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_project_for_user(db, current_user, project_id)
    return db.query(Proposal).filter(Proposal.project_id == project_id).order_by(Proposal.created_at.desc()).all()


@router.get("/projects/{project_id}/proposals/latest", response_model=ProposalRead)
def latest_project_proposal(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_project_for_user(db, current_user, project_id)
    proposal = db.query(Proposal).filter(Proposal.project_id == project_id).order_by(Proposal.created_at.desc()).first()
    if not proposal:
        raise not_found("Proposal not found")
    return proposal
