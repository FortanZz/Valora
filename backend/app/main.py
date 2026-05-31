from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import get_settings
from app.exceptions import format_validation_errors
from app.database import init_db
from app.routers.auth import router as auth_router
from app.routers.properties import router as properties_router


settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

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

app.include_router(auth_router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
app.include_router(properties_router, prefix=f"{settings.api_prefix}/properties", tags=["properties"])


@app.get(f"{settings.api_prefix}/health")
def health_check() -> dict:
    return {"status": "ok", "service": settings.app_name}
