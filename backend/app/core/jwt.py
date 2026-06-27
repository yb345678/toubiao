"""Small JWT implementation using the standard library.

The project can later switch to python-jose or PyJWT without changing the API
surface used by route handlers.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from app.core.config import settings


logger = logging.getLogger("ai_bidding.auth")


class TokenDecodeError(ValueError):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_token(
    subject: str,
    token_type: str,
    expires_minutes: int,
    extra_claims: Dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=expires_minutes)
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": subject, "exp": int(expires.timestamp()), "iat": int(now.timestamp()), "typ": token_type}
    if extra_claims:
        payload.update(extra_claims)
    signing_input = f"{_b64encode(json.dumps(header).encode())}.{_b64encode(json.dumps(payload).encode())}"
    signature = hmac.new(settings.secret_key.encode(), signing_input.encode(), hashlib.sha256).digest()
    logger.info(
        "jwt_created type=%s subject=%s expires_at=%s has_secret=%s",
        token_type,
        subject,
        expires.isoformat(),
        bool(settings.secret_key),
    )
    return f"{signing_input}.{_b64encode(signature)}"


def create_access_token(subject: str, expires_minutes: int | None = None, extra_claims: Dict[str, Any] | None = None) -> str:
    return create_token(
        subject,
        "access",
        expires_minutes or settings.access_token_expire_minutes,
        extra_claims,
    )


def create_refresh_token(subject: str, expires_minutes: int | None = None, extra_claims: Dict[str, Any] | None = None) -> str:
    return create_token(
        subject,
        "refresh",
        expires_minutes or settings.refresh_token_expire_minutes,
        extra_claims,
    )


def _legacy_create_access_token(subject: str, expires_minutes: int | None = None, extra_claims: Dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": subject, "exp": int(expires.timestamp()), "iat": int(now.timestamp())}
    if extra_claims:
        payload.update(extra_claims)
    signing_input = f"{_b64encode(json.dumps(header).encode())}.{_b64encode(json.dumps(payload).encode())}"
    signature = hmac.new(settings.secret_key.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_b64encode(signature)}"


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".", 2)
    except ValueError as exc:
        logger.warning("jwt_decode_failed reason=malformed_token")
        raise TokenDecodeError("malformed_token") from exc

    try:
        signing_input = f"{header_b64}.{payload_b64}"
        expected = hmac.new(settings.secret_key.encode(), signing_input.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64decode(signature_b64)):
            logger.warning("jwt_decode_failed reason=invalid_signature")
            raise TokenDecodeError("invalid_signature")
        payload = json.loads(_b64decode(payload_b64))
        token_type = payload.get("typ")
        if token_type and token_type != "access":
            logger.warning("jwt_decode_failed reason=wrong_token_type type=%s", token_type)
            raise TokenDecodeError("wrong_token_type")
        if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
            logger.warning("jwt_decode_failed reason=token_expired subject=%s", payload.get("sub"))
            raise TokenDecodeError("token_expired")
        if not payload.get("sub"):
            logger.warning("jwt_decode_failed reason=missing_subject")
            raise TokenDecodeError("missing_subject")
        return payload
    except TokenDecodeError:
        raise
    except Exception as exc:
        logger.warning("jwt_decode_failed reason=invalid_token")
        raise TokenDecodeError("invalid_token") from exc


def decode_refresh_token(token: str) -> Dict[str, Any]:
    payload = decode_access_token_allow_type(token)
    if payload.get("typ") != "refresh":
        logger.warning("jwt_decode_failed reason=invalid_refresh_token_type type=%s", payload.get("typ"))
        raise TokenDecodeError("invalid_refresh_token")
    return payload


def decode_access_token_allow_type(token: str) -> Dict[str, Any]:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".", 2)
    except ValueError as exc:
        logger.warning("jwt_decode_failed reason=malformed_token")
        raise TokenDecodeError("malformed_token") from exc

    try:
        signing_input = f"{header_b64}.{payload_b64}"
        expected = hmac.new(settings.secret_key.encode(), signing_input.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64decode(signature_b64)):
            logger.warning("jwt_decode_failed reason=invalid_signature")
            raise TokenDecodeError("invalid_signature")
        payload = json.loads(_b64decode(payload_b64))
        if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
            logger.warning("jwt_decode_failed reason=token_expired subject=%s", payload.get("sub"))
            raise TokenDecodeError("token_expired")
        if not payload.get("sub"):
            logger.warning("jwt_decode_failed reason=missing_subject")
            raise TokenDecodeError("missing_subject")
        return payload
    except TokenDecodeError:
        raise
    except Exception as exc:
        logger.warning("jwt_decode_failed reason=invalid_token")
        raise TokenDecodeError("invalid_token") from exc
