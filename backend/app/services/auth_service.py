from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import bad_request, unauthorized
from app.core.config import settings
from app.core.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest


def register_user(db: Session, payload: RegisterRequest) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise bad_request("Email already registered")
    user = User(email=payload.email, username=payload.username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _build_token_pair(user: User) -> dict[str, str | int]:
    claims = {"role": user.role, "email": user.email}
    return {
        "access_token": create_access_token(user.id, extra_claims=claims),
        "refresh_token": create_refresh_token(user.id, extra_claims=claims),
        "expires_in": settings.access_token_expire_minutes * 60,
        "refresh_expires_in": settings.refresh_token_expire_minutes * 60,
    }


def login_user(db: Session, email: str, password: str) -> dict[str, str | int]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise unauthorized("Invalid email or password")
    if user.status != "active":
        raise unauthorized("User is disabled")
    return _build_token_pair(user)


def refresh_user_token(db: Session, refresh_token: str) -> dict[str, str | int]:
    try:
        payload = decode_refresh_token(refresh_token)
    except ValueError:
        raise unauthorized("Invalid refresh token")
    user = db.get(User, payload.get("sub"))
    if not user:
        raise unauthorized("User not found")
    if user.status != "active":
        raise unauthorized("User is disabled")
    return _build_token_pair(user)
