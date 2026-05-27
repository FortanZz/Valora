from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt_handler import decode_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_token(token, expected_type="access")

    try:
        return int(payload["sub"])
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
