"""FastAPI application entrypoint."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.handlers import register_exception_handlers
from app.db.init_db import init_db


def mount_spa(app: FastAPI) -> None:
    if not settings.static_dir:
        return

    static_dir = Path(settings.static_dir)
    index_file = static_dir / "index.html"
    assets_dir = static_dir / "assets"
    if not index_file.exists():
        return

    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str):
        requested = static_dir / full_path
        if full_path and requested.is_file():
            return FileResponse(str(requested))
        return FileResponse(str(index_file))


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
    mount_spa(app)
    return app


app = create_app()
