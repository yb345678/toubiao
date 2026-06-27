"""Application configuration.

The settings are intentionally lightweight and environment-variable driven so
the backend can run locally, in Docker, or in a hackathon demo environment.
"""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass


def _is_vercel() -> bool:
    return os.getenv("VERCEL") == "1"


def _secret_key() -> str:
    value = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY")
    if value:
        return value
    if _is_vercel():
        raise RuntimeError("JWT_SECRET must be configured in Vercel environment variables.")
    return secrets.token_urlsafe(32)


def _default_database_url() -> str:
    if _is_vercel():
        return "sqlite:////tmp/ai-bidding-vercel.db"
    return "sqlite:///./database/app.db"


def _default_upload_dir() -> str:
    return "/tmp/uploads" if _is_vercel() else "./uploads"


def _default_output_dir() -> str:
    return "/tmp/outputs" if _is_vercel() else "./outputs"


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "AI Bidding Multi-Agent Platform")
    api_v1_prefix: str = os.getenv("API_V1_PREFIX", "/api/v1")
    secret_key: str = _secret_key()
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    refresh_token_expire_minutes: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "10080"))
    database_url: str = os.getenv("DATABASE_URL", _default_database_url())
    upload_dir: str = os.getenv("UPLOAD_DIR", _default_upload_dir())
    output_dir: str = os.getenv("OUTPUT_DIR", _default_output_dir())
    blob_read_write_token: str = os.getenv("BLOB_READ_WRITE_TOKEN", "")
    static_dir: str = os.getenv("STATIC_DIR", "")
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    frontend_url: str = os.getenv("FRONTEND_URL", "")
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))


settings = Settings()
