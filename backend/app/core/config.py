"""Application configuration.

The settings are intentionally lightweight and environment-variable driven so
the backend can run locally, in Docker, or in a hackathon demo environment.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "AI Bidding Multi-Agent Platform")
    api_v1_prefix: str = os.getenv("API_V1_PREFIX", "/api/v1")
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    refresh_token_expire_minutes: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "10080"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./database/app.db")
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    output_dir: str = os.getenv("OUTPUT_DIR", "./outputs")
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))


settings = Settings()
