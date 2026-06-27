from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import not_found
from app.db.session import get_db
from app.models.analysis import Analysis
from app.models.user import User
from app.schemas.report import ReportRead
from app.services.analysis_service import get_latest_analysis
from app.services.export_service import (
    export_all,
    export_proposal_markdown,
    export_proposal_word,
    export_qualification_excel,
    export_risk_pdf,
)
from app.services.project_service import get_project_for_user


router = APIRouter()


@router.get("/projects/{project_id}/reports/latest", response_model=ReportRead)
def latest_report(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_project_for_user(db, current_user, project_id)
    analysis = get_latest_analysis(db, project_id)
    if not analysis or not analysis.final_report_json:
        raise not_found("Report not found")
    return ReportRead(analysis_id=analysis.id, project_id=project_id, final_report=json.loads(analysis.final_report_json))


@router.get("/reports/{analysis_id}", response_model=ReportRead)
def get_report(analysis_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    analysis = db.get(Analysis, analysis_id)
    if not analysis or not analysis.final_report_json:
        raise not_found("Report not found")
    get_project_for_user(db, current_user, analysis.project_id)
    return ReportRead(analysis_id=analysis.id, project_id=analysis.project_id, final_report=json.loads(analysis.final_report_json))


def _latest_analysis_for_export(project_id: str, db: Session, current_user: User) -> tuple[object, object]:
    project = get_project_for_user(db, current_user, project_id)
    analysis = get_latest_analysis(db, project_id)
    if not analysis or not analysis.final_report_json:
        raise not_found("Completed report not found")
    return project, analysis


@router.get("/projects/{project_id}/exports/qualification-excel")
def export_qualification_excel_api(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project, analysis = _latest_analysis_for_export(project_id, db, current_user)
    path = export_qualification_excel(project, analysis)
    return FileResponse(str(path), filename=path.name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.get("/projects/{project_id}/exports/risk-pdf")
def export_risk_pdf_api(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project, analysis = _latest_analysis_for_export(project_id, db, current_user)
    path = export_risk_pdf(project, analysis)
    return FileResponse(str(path), filename=path.name, media_type="application/pdf")


@router.get("/projects/{project_id}/exports/proposal-markdown")
def export_proposal_markdown_api(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project, analysis = _latest_analysis_for_export(project_id, db, current_user)
    path = export_proposal_markdown(project, analysis)
    return FileResponse(str(path), filename=path.name, media_type="text/markdown")


@router.get("/projects/{project_id}/exports/proposal-word")
def export_proposal_word_api(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project, analysis = _latest_analysis_for_export(project_id, db, current_user)
    path = export_proposal_word(project, analysis)
    return FileResponse(str(path), filename=path.name, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@router.get("/projects/{project_id}/exports/all")
def export_all_api(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project, analysis = _latest_analysis_for_export(project_id, db, current_user)
    path = export_all(project, analysis)
    return FileResponse(str(path), filename=path.name, media_type="application/zip")
