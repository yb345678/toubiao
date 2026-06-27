from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.history import History
from app.models.user import User
from app.schemas.history import HistoryRead


router = APIRouter()


@router.get("/history", response_model=list[HistoryRead])
def list_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(History)
        .filter(History.user_id == current_user.id)
        .order_by(History.created_at.desc())
        .limit(100)
        .all()
    )
