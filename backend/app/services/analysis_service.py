from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.agents.orchestrator import run_analysis_workflow
from app.core.config import settings
from app.core.exceptions import DatabaseError, bad_request
from app.models.analysis import Analysis
from app.models.project import Project
from app.models.user import User
from app.services.persistence_service import persist_proposal, persist_risks, record_history, record_log
from app.services.blob_service import download_url_to_tmp, remove_tmp_file
from app.services.file_service import missing_required_files


def start_analysis(db: Session, user: User, project: Project) -> Analysis:
    missing = missing_required_files(project)
    if missing:
        raise bad_request("Missing required files: " + "、".join(missing))

    analysis = Analysis(
        project_id=project.id,
        started_by=user.id,
        status="running",
        progress=5,
        current_step="router_started",
        started_at=datetime.utcnow(),
    )
    db.add(analysis)
    record_history(
        db,
        user=user,
        project=project,
        analysis=analysis,
        action="analysis_started",
        target_type="analysis",
        target_id=analysis.id,
        description="Multi-agent bidding analysis started.",
    )
    record_log(
        db,
        user=user,
        project=project,
        analysis=analysis,
        module="router",
        event="analysis_started",
        message="WorkflowRouter started.",
    )
    try:
        db.commit()
        db.refresh(analysis)
    except SQLAlchemyError as exc:
        db.rollback()
        raise DatabaseError("Failed to create analysis task") from exc

    try:
        def update_progress(step: str, progress: int) -> None:
            analysis.current_step = step
            analysis.progress = progress
            try:
                db.commit()
            except SQLAlchemyError:
                db.rollback()

        tender_tmp = None
        qualification_tmp = None
        try:
            tender_tmp = download_url_to_tmp(project.tender_file_url, Path(project.tender_file_name or "tender.pdf").suffix, "tender_pdf")
            qualification_tmp = download_url_to_tmp(
                project.qualification_file_url,
                Path(project.qualification_file_name or "qualification.xlsx").suffix,
                "qualification_file",
            )
            result = run_analysis_workflow(str(tender_tmp), str(qualification_tmp), progress_callback=update_progress)
        finally:
            remove_tmp_file(tender_tmp)
            remove_tmp_file(qualification_tmp)
        analysis.status = "completed"
        analysis.progress = 100
        analysis.current_step = "completed"
        analysis.score = result["decision"]["score"]
        analysis.recommendation = result["decision"]["recommendation"]
        analysis.summary = result["decision"].get("summary")
        analysis.parsed_document_json = json.dumps(result["agents"]["pdf_parser"], ensure_ascii=False)
        analysis.qualification_result_json = json.dumps(result["agents"]["qualification_matcher"], ensure_ascii=False)
        analysis.risk_result_json = json.dumps(result["agents"]["risk_reviewer"], ensure_ascii=False)
        analysis.proposal_result_json = json.dumps(result["agents"]["proposal_writer"], ensure_ascii=False)
        analysis.final_report_json = json.dumps(result, ensure_ascii=False)
        persist_risks(db, project, analysis, result["agents"]["risk_reviewer"])
        persist_proposal(db, project, analysis, result["agents"]["proposal_writer"])
        analysis.finished_at = datetime.utcnow()
        project.status = "completed"
        project.latest_score = analysis.score
        project.latest_recommendation = analysis.recommendation
        project.latest_analysis_id = analysis.id
        record_history(
            db,
            user=user,
            project=project,
            analysis=analysis,
            action="analysis_completed",
            target_type="analysis",
            target_id=analysis.id,
            description="Multi-agent bidding analysis completed and persisted.",
            after={"score": analysis.score, "recommendation": analysis.recommendation},
        )
        record_log(
            db,
            user=user,
            project=project,
            analysis=analysis,
            module="router",
            event="analysis_completed",
            message="WorkflowRouter completed and persisted report, risks, and proposal.",
            metadata={"score": analysis.score, "recommendation": analysis.recommendation},
        )
    except Exception as exc:
        analysis.status = "failed"
        analysis.error_message = str(exc)
        analysis.finished_at = datetime.utcnow()
        project.status = "failed"
        record_history(
            db,
            user=user,
            project=project,
            analysis=analysis,
            action="analysis_failed",
            target_type="analysis",
            target_id=analysis.id,
            description=str(exc),
        )
        record_log(
            db,
            user=user,
            project=project,
            analysis=analysis,
            level="error",
            module="router",
            event="analysis_failed",
            message=str(exc),
        )

    try:
        db.commit()
        db.refresh(analysis)
    except SQLAlchemyError as exc:
        db.rollback()
        raise DatabaseError("Failed to persist analysis result") from exc
    return analysis


def get_latest_analysis(db: Session, project_id: str) -> Analysis | None:
    return db.query(Analysis).filter(Analysis.project_id == project_id).order_by(Analysis.created_at.desc()).first()


def write_report_file(analysis: Analysis) -> str:
    output = Path(settings.output_dir) / analysis.project_id
    output.mkdir(parents=True, exist_ok=True)
    path = output / f"analysis_{analysis.id}.json"
    path.write_text(analysis.final_report_json or "{}", encoding="utf-8")
    return str(path)
