"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.handlers import register_exception_handlers
from app.db.init_db import init_db


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")
    configured_origins = [
        item.strip().rstrip("/")
        for item in settings.cors_origins.split(",")
        if item.strip() and item.strip() != "*"
    ]
    if settings.frontend_url:
        configured_origins.append(settings.frontend_url.strip().rstrip("/"))
    origins = sorted(set(configured_origins)) or ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=origins != ["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    @app.get("/health")
    def health():
        return {"status": "ok", "service": settings.app_name}

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
