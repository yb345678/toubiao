from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.enterprise import EnterpriseCreate, EnterpriseRead
from app.schemas.project import ProjectCreate, ProjectRead
from app.services.project_service import create_enterprise, create_project, get_project_for_user, list_enterprises, list_projects


router = APIRouter()


@router.post("/enterprises", response_model=EnterpriseRead)
def create_enterprise_api(payload: EnterpriseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_enterprise(db, current_user, payload)


@router.get("/enterprises", response_model=list[EnterpriseRead])
def list_enterprise_api(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_enterprises(db, current_user)


@router.post("", response_model=ProjectRead)
def create_project_api(payload: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_project(db, current_user, payload)


@router.get("", response_model=list[ProjectRead])
def list_project_api(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_projects(db, current_user)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project_api(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_project_for_user(db, current_user, project_id)
