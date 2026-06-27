"""FastAPI dependencies."""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import unauthorized
from app.core.jwt import decode_access_token
from app.db.session import get_db
from app.models.user import User


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized("Missing bearer token")
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError:
        raise unauthorized("Invalid token")
    user = db.get(User, payload.get("sub"))
    if not user:
        raise unauthorized("User not found")
    if user.status != "active":
        raise unauthorized("User is disabled")
    return user
