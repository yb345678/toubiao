"""FastAPI dependencies."""

from __future__ import annotations

import logging

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import unauthorized
from app.core.jwt import TokenDecodeError, decode_access_token
from app.db.session import get_db
from app.models.user import User


bearer_scheme = HTTPBearer(auto_error=False)
logger = logging.getLogger("ai_bidding.auth")


def _restore_token_user(db: Session, payload: dict) -> User | None:
    user_id = payload.get("sub")
    email = payload.get("email")
    if not user_id or not email:
        return None

    username = str(email).split("@", 1)[0] or "token_user"
    user = User(
        id=user_id,
        email=email,
        username=username,
        password_hash="token-restored-user",
        role=payload.get("role") or "user",
        status="active",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.warning("auth_user_restored_from_valid_token user_id=%s email=%s", user_id, email)
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        logger.warning("auth_failed reason=missing_bearer_token")
        raise unauthorized("Missing bearer token")
    try:
        payload = decode_access_token(credentials.credentials)
    except TokenDecodeError as exc:
        logger.warning("auth_failed reason=%s", exc.reason)
        raise unauthorized(f"Invalid token: {exc.reason}")
    user = db.get(User, payload.get("sub"))
    if not user:
        user = _restore_token_user(db, payload)
    if not user:
        logger.warning("auth_failed reason=user_not_found subject=%s", payload.get("sub"))
        raise unauthorized("User not found")
    if user.status != "active":
        logger.warning("auth_failed reason=user_disabled subject=%s", payload.get("sub"))
        raise unauthorized("User is disabled")
    return user
