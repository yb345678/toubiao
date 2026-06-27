"""Import all ORM models so metadata registration works."""

from app.models.analysis import Analysis
from app.models.enterprise import Enterprise
from app.models.history import History
from app.models.log import Log
from app.models.notification import Notification
from app.models.project import Project
from app.models.proposal import Proposal
from app.models.qualification import Qualification
from app.models.risk import Risk
from app.models.user import User

__all__ = [
    "Analysis",
    "Enterprise",
    "History",
    "Log",
    "Notification",
    "Project",
    "Proposal",
    "Qualification",
    "Risk",
    "User",
]
