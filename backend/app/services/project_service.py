from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import not_found
from app.models.enterprise import Enterprise
from app.models.project import Project
from app.models.user import User
from app.schemas.enterprise import EnterpriseCreate
from app.schemas.project import ProjectCreate
from app.services.persistence_service import record_history, record_log
from app.services.file_service import project_files_ready


def create_enterprise(db: Session, user: User, payload: EnterpriseCreate) -> Enterprise:
    enterprise = Enterprise(owner_user_id=user.id, **payload.model_dump())
    db.add(enterprise)
    record_history(
        db,
        user=user,
        action="enterprise_created",
        target_type="enterprise",
        target_id=enterprise.id,
        description=f"Enterprise created: {enterprise.name}",
    )
    db.commit()
    db.refresh(enterprise)
    return enterprise


def list_enterprises(db: Session, user: User) -> list[Enterprise]:
    return db.query(Enterprise).filter(Enterprise.owner_user_id == user.id, Enterprise.deleted_at.is_(None)).all()


def create_project(db: Session, user: User, payload: ProjectCreate) -> Project:
    enterprise = db.get(Enterprise, payload.enterprise_id)
    if not enterprise or enterprise.owner_user_id != user.id:
        raise not_found("Enterprise not found")
    project = Project(created_by=user.id, **payload.model_dump())
    db.add(project)
    record_history(
        db,
        user=user,
        project=project,
        action="project_created",
        target_type="project",
        target_id=project.id,
        description=f"Project created: {project.name}",
    )
    record_log(
        db,
        user=user,
        project=project,
        module="project",
        event="project_created",
        message=f"Project created: {project.name}",
    )
    db.commit()
    db.refresh(project)
    return project


def normalize_project_status(project: Project) -> Project:
    if project.status in {"created", "draft", "partial_uploaded", "uploaded"}:
        if project_files_ready(project):
            project.status = "uploaded"
        elif project.tender_file_url or project.qualification_file_url:
            project.status = "partial_uploaded"
        else:
            project.status = "created"
    return project


def list_projects(db: Session, user: User) -> list[Project]:
    projects = (
        db.query(Project)
        .join(Enterprise, Project.enterprise_id == Enterprise.id)
        .filter(Enterprise.owner_user_id == user.id, Project.deleted_at.is_(None))
        .order_by(Project.created_at.desc())
        .all()
    )
    for project in projects:
        normalize_project_status(project)
    return projects


def get_project_for_user(db: Session, user: User, project_id: str) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise not_found("Project not found")
    enterprise = db.get(Enterprise, project.enterprise_id)
    if not enterprise or enterprise.owner_user_id != user.id:
        raise not_found("Project not found")
    return normalize_project_status(project)
