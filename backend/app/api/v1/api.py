from fastapi import APIRouter

from app.modules.health.routes import router as health_router
from app.routers.affidavit_router import router as affidavit_router
from app.routers.auth_router import router as auth_router
from app.routers.client_router import router as client_router
from app.routers.template_router import router as template_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(template_router)
api_router.include_router(client_router)
api_router.include_router(affidavit_router)
