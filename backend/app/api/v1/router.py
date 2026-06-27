"""API v1 router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import analysis, auth, dashboard, files, history, projects, proposals, reports, risks, users


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(files.router, prefix="/projects", tags=["files"])
api_router.include_router(analysis.router, tags=["analysis"])
api_router.include_router(reports.router, tags=["reports"])
api_router.include_router(risks.router, tags=["risks"])
api_router.include_router(proposals.router, tags=["proposals"])
api_router.include_router(history.router, tags=["history"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
