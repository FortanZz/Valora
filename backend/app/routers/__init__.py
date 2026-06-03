"""API routers for Valora."""

from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.favorites import router as favorites_router
from app.routers.messages import router as messages_router
from app.routers.properties import router as properties_router

# Routers that define their own prefix and tags (e.g. /api/v1/*).
# Register these in main via: for router in api_v1_routers: app.include_router(router)
api_v1_routers: list[APIRouter] = [
    properties_router,
    favorites_router,
    messages_router,
]

__all__ = [
    "auth_router",
    "favorites_router",
    "messages_router",
    "properties_router",
    "api_v1_routers",
]
