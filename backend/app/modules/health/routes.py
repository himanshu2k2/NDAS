from fastapi import APIRouter

from app.core.responses import ok
from app.db.mongo import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    await get_db().command("ping")
    return ok({"status": "ok", "db": "connected"})
