from fastapi import APIRouter

from app.modules.health.routes import router as health_router
from app.routers.auth_router import router as auth_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(auth_router)
