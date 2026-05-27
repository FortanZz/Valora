from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.auth.dependencies import get_current_user_id
from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.schemas.user import UserLogin, UserRegister, UserResponse


router = APIRouter()


@dataclass
class StoredUser:
    id: int
    email: str
    first_name: str
    last_name: str
    hashed_password: str
    created_at: datetime


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


USERS_BY_EMAIL: Dict[str, StoredUser] = {}
USERS_BY_ID: Dict[int, StoredUser] = {}


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister) -> AuthResponse:
    email = _normalize_email(payload.email)
    if email in USERS_BY_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    user = StoredUser(
        id=len(USERS_BY_ID) + 1,
        email=email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        hashed_password=get_password_hash(payload.password),
        created_at=datetime.utcnow(),
    )
    USERS_BY_EMAIL[email] = user
    USERS_BY_ID[user.id] = user

    return _build_auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin) -> AuthResponse:
    user = USERS_BY_EMAIL.get(_normalize_email(payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _build_auth_response(user)


@router.post("/refresh", response_model=AuthResponse)
def refresh(payload: RefreshTokenRequest) -> AuthResponse:
    token_payload = decode_token(payload.refresh_token, expected_type="refresh")
    try:
        user_id = int(token_payload["sub"])
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = USERS_BY_ID.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _build_auth_response(user)


@router.get("/me", response_model=UserResponse)
def get_me(current_user_id: int = Depends(get_current_user_id)) -> UserResponse:
    user = USERS_BY_ID.get(current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _to_user_response(user)


def _build_auth_response(user: StoredUser) -> AuthResponse:
    subject = str(user.id)
    claims = {"email": user.email}
    return AuthResponse(
        access_token=create_access_token(subject=subject, extra_claims=claims),
        refresh_token=create_refresh_token(subject=subject, extra_claims=claims),
        user=_to_user_response(user),
    )


def _to_user_response(user: StoredUser) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        created_at=user.created_at,
    )


def _normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if "@" not in normalized:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A valid email address is required",
        )

    return normalized
