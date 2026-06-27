"""Small JWT implementation using the standard library.

The project can later switch to python-jose or PyJWT without changing the API
surface used by route handlers.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict

from app.core.config import settings


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
    expires = int(time.time()) + 60 * expires_minutes
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": subject, "exp": expires, "iat": int(time.time()), "typ": token_type}
    if extra_claims:
        payload.update(extra_claims)
    signing_input = f"{_b64encode(json.dumps(header).encode())}.{_b64encode(json.dumps(payload).encode())}"
    signature = hmac.new(settings.secret_key.encode(), signing_input.encode(), hashlib.sha256).digest()
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
    expires = int(time.time()) + 60 * (expires_minutes or settings.access_token_expire_minutes)
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": subject, "exp": expires, "iat": int(time.time())}
    if extra_claims:
        payload.update(extra_claims)
    signing_input = f"{_b64encode(json.dumps(header).encode())}.{_b64encode(json.dumps(payload).encode())}"
    signature = hmac.new(settings.secret_key.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_b64encode(signature)}"


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".", 2)
        signing_input = f"{header_b64}.{payload_b64}"
        expected = hmac.new(settings.secret_key.encode(), signing_input.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64decode(signature_b64)):
            raise ValueError("invalid signature")
        payload = json.loads(_b64decode(payload_b64))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("token expired")
        return payload
    except Exception as exc:
        raise ValueError("invalid token") from exc


def decode_refresh_token(token: str) -> Dict[str, Any]:
    payload = decode_access_token(token)
    if payload.get("typ") != "refresh":
        raise ValueError("invalid refresh token")
    return payload
