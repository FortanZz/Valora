from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import bcrypt
import jwt
from fastapi import HTTPException, status

from app.config import get_settings


settings = get_settings()


def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(
    subject: str,
    extra_claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    return _create_token(
        subject=subject,
        token_type="access",
        extra_claims=extra_claims,
        expires_delta=expires_delta
        or timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )


def create_refresh_token(
    subject: str,
    extra_claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    return _create_token(
        subject=subject,
        token_type="refresh",
        extra_claims=extra_claims,
        expires_delta=expires_delta
        or timedelta(days=settings.jwt_refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise credentials_error from exc

    if expected_type and payload.get("type") != expected_type:
        raise credentials_error

    if not payload.get("sub"):
        raise credentials_error

    return payload


def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    now = datetime.utcnow()
    payload: Dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
