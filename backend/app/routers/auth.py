from datetime import datetime
from typing import Any, Dict

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
from app.database import create_user, get_user_by_email, get_user_by_id
from app.schemas.user import UserLogin, UserRegister, UserResponse


router = APIRouter()


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse



@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister) -> AuthResponse:
    email = _normalize_email(payload.email)
    if get_user_by_email(email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )
    user_data = create_user(
        email=email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        hashed_password=get_password_hash(payload.password),
        created_at=datetime.utcnow(),
    )
    return _build_auth_response(user_data)


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin) -> AuthResponse:
    user_data = get_user_by_email(_normalize_email(payload.email))
    if not user_data or not verify_password(payload.password, user_data["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _build_auth_response(user_data)


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

    user_data = get_user_by_id(user_id)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _build_auth_response(user_data)


@router.get("/me", response_model=UserResponse)
def get_me(current_user_id: int = Depends(get_current_user_id)) -> UserResponse:
    user_data = get_user_by_id(current_user_id)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _to_user_response(user_data)


def _build_auth_response(user: Dict[str, Any]) -> AuthResponse:
    subject = str(user["id"])
    claims = {"email": user["email"]}
    return AuthResponse(
        access_token=create_access_token(subject=subject, extra_claims=claims),
        refresh_token=create_refresh_token(subject=subject, extra_claims=claims),
        user=_to_user_response(user),
    )

def _to_user_response(user: Dict[str, Any]) -> UserResponse:
    return UserResponse(
        id=user["id"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        created_at=user["created_at"],
    )


def _normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if "@" not in normalized:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A valid email address is required",
        )

    return normalized
