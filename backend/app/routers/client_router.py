from typing import Optional

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_current_user
from app.core.responses import ok
from app.db.mongo import get_db
from app.schemas.client_schema import ClientCreate, ClientUpdate
from app.services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("", status_code=201)
async def create_client(
    payload: ClientCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    record = await ClientService.create(db, current_user, payload)
    return ok(record.model_dump(), message="Client created.")


@router.get("")
async def list_clients(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    result = await ClientService.list_clients(db, search, page, page_size)
    return ok(result.model_dump())


@router.get("/{client_id}")
async def get_client(
    client_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    record = await ClientService.get_by_id(db, client_id)
    return ok(record.model_dump())


@router.put("/{client_id}")
async def update_client(
    client_id: str,
    payload: ClientUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    record = await ClientService.update(db, client_id, payload)
    return ok(record.model_dump(), message="Client updated.")


@router.delete("/{client_id}")
async def delete_client(
    client_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    await ClientService.delete(db, client_id)
    return ok(None, message="Client deleted.")
