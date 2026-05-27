from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import get_settings
from app.routers import auth
from app.exceptions import format_validation_errors


settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": format_validation_errors(exc.errors()),
            "errors": exc.errors()
        }
    )

app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])


@app.get(f"{settings.api_prefix}/health")
def health_check() -> dict:
    return {"status": "ok", "service": settings.app_name}
