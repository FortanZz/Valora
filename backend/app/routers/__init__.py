"""API routers for Valora."""

from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.properties import router as properties_router

# Routers that define their own prefix and tags (e.g. /api/v1/*).
# Register these in main via: for router in api_v1_routers: app.include_router(router)
api_v1_routers: list[APIRouter] = [
    properties_router,
]

__all__ = [
    "auth_router",
    "properties_router",
    "api_v1_routers",
]
