from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.enterprise import Enterprise
from app.models.project import Project
from app.models.user import User


def get_summary(db: Session, user: User) -> dict:
    enterprise_ids = [item.id for item in db.query(Enterprise).filter(Enterprise.owner_user_id == user.id).all()]
    project_count = db.query(Project).filter(Project.enterprise_id.in_(enterprise_ids)).count() if enterprise_ids else 0
    completed_count = db.query(Project).filter(Project.enterprise_id.in_(enterprise_ids), Project.status == "completed").count() if enterprise_ids else 0
    running_count = db.query(Analysis).join(Project, Analysis.project_id == Project.id).filter(Project.enterprise_id.in_(enterprise_ids), Analysis.status == "running").count() if enterprise_ids else 0
    return {"project_count": project_count, "completed_count": completed_count, "running_count": running_count}
