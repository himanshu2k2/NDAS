from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.mongo import close_db, connect_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.storage_path.mkdir(parents=True, exist_ok=True)
    for name in ("clients", "documents", "templates"):
        (settings.storage_path / name).mkdir(parents=True, exist_ok=True)
    await connect_db()
    yield
    await close_db()


app = FastAPI(title="NDAOMS API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"success": True, "data": {"name": "NDAOMS API"}}