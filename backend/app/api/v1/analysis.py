from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.analysis import Analysis
from app.models.user import User
from app.schemas.analysis import AnalysisRead, AnalysisStartResponse
from app.services.analysis_service import start_analysis
from app.services.project_service import get_project_for_user


router = APIRouter()


@router.post("/projects/{project_id}/analysis/start", response_model=AnalysisStartResponse)
def start_analysis_api(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_project_for_user(db, current_user, project_id)
    analysis = start_analysis(db, current_user, project)
    return AnalysisStartResponse(task_id=analysis.id, status=analysis.status)


@router.get("/analysis-tasks/{analysis_id}", response_model=AnalysisRead)
def get_analysis_api(analysis_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    analysis = db.get(Analysis, analysis_id)
    if not analysis:
        from app.core.exceptions import not_found

        raise not_found("Analysis not found")
    get_project_for_user(db, current_user, analysis.project_id)
    return analysis
