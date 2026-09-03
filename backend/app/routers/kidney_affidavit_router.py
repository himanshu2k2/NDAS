from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.responses import ok
from app.db.mongo import get_db
from app.schemas.kidney_affidavit_schema import KidneyAffidavitCreate, KidneyAffidavitUpdate
from app.services.kidney_affidavit_service import KidneyAffidavitService

router = APIRouter(prefix="/kidney-affidavits", tags=["kidney-affidavits"])


@router.post("", status_code=201)
async def create_affidavit(
    payload: KidneyAffidavitCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    record = await KidneyAffidavitService.create(db, payload)
    return ok(record.model_dump(), message="Affidavit created.")


@router.get("/{affidavit_id}")
async def get_affidavit(
    affidavit_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    record = await KidneyAffidavitService.get_by_id(db, affidavit_id)
    return ok(record.model_dump())


@router.get("")
async def list_affidavits(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    result = await KidneyAffidavitService.list_affidavits(db, search, page, page_size)
    return ok(result.model_dump())


@router.put("/{affidavit_id}")
async def update_affidavit(
    affidavit_id: str,
    payload: KidneyAffidavitUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    record = await KidneyAffidavitService.update(db, affidavit_id, payload)
    return ok(record.model_dump(), message="Affidavit updated.")


@router.delete("/{affidavit_id}")
async def delete_affidavit(
    affidavit_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    await KidneyAffidavitService.delete(db, affidavit_id)
    return ok(None, message="Affidavit deleted.")


@router.post("/{affidavit_id}/generate-docx")
async def generate_docx(
    affidavit_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> StreamingResponse:
    buf = await KidneyAffidavitService.generate_docx(db, affidavit_id)
    filename = f"kidney_affidavit_{affidavit_id}.docx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{affidavit_id}/generate-pdf")
async def generate_pdf(
    affidavit_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> StreamingResponse:
    buf = await KidneyAffidavitService.generate_pdf(db, affidavit_id)
    filename = f"kidney_affidavit_{affidavit_id}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
