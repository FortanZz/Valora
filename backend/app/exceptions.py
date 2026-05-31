from fastapi import HTTPException, status
from pydantic import ValidationError
from typing import Any, Dict, List


class ValidationException(HTTPException):
    """Custom validation error"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class InvalidCredentialsException(HTTPException):
    """Invalid login credentials"""
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class UserAlreadyExistsException(HTTPException):
    """User already exists error"""
    def __init__(self, detail: str = "User with this email already exists"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class NotFoundException(HTTPException):
    """Resource not found error"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class UnauthorizedException(HTTPException):
    """User not authorized to perform action"""
    def __init__(self, detail: str = "Not authorized to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class PropertyConstraintException(HTTPException):
    """Property business logic constraint violation"""
    def __init__(self, detail: str = "Property constraint violation"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class DatabaseException(HTTPException):
    """Database operation error"""
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


def format_validation_errors(errors: List[Dict[str, Any]]) -> str:
    """Format Pydantic validation errors into readable message"""
    messages = []
    for error in errors:
        field = ".".join(str(x) for x in error.get("loc", []))
        msg = error.get("msg", "Validation error")
        messages.append(f"{field}: {msg}")
    return "; ".join(messages)
