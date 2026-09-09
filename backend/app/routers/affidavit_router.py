from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_current_user
from app.core.responses import ok
from app.db.mongo import get_db
from app.schemas.affidavit_schema import AffidavitCreate
from app.services.affidavit_service import AffidavitService

router = APIRouter(prefix="/affidavits", tags=["affidavits"])

DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@router.post("", status_code=201)
async def create_affidavit(
    payload: AffidavitCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    record = await AffidavitService.create(db, current_user, payload)
    return ok(record.model_dump(), message="Affidavit generated successfully.")


@router.get("")
async def list_affidavits(
    search: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    template_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    result = await AffidavitService.list_affidavits(db, search, client_id, template_id, status, page, page_size)
    return ok(result.model_dump())


@router.get("/{affidavit_id}")
async def get_affidavit(
    affidavit_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    record = await AffidavitService.get_by_id(db, affidavit_id)
    return ok(record.model_dump())


@router.get("/{affidavit_id}/download")
async def download_affidavit(
    affidavit_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> FileResponse:
    path, filename = await AffidavitService.get_download_info(db, affidavit_id)
    return FileResponse(path, media_type=DOCX_MEDIA_TYPE, filename=filename)


@router.delete("/{affidavit_id}")
async def delete_affidavit(
    affidavit_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    await AffidavitService.delete(db, affidavit_id)
    return ok(None, message="Affidavit deleted.")
