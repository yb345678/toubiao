from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.risk import Risk
from app.models.user import User
from app.schemas.risk import RiskRead
from app.services.project_service import get_project_for_user


router = APIRouter()


@router.get("/projects/{project_id}/risks", response_model=list[RiskRead])
def list_project_risks(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_project_for_user(db, current_user, project_id)
    return db.query(Risk).filter(Risk.project_id == project_id).order_by(Risk.created_at.desc()).all()
