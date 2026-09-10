from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_current_user
from app.core.responses import ok
from app.db.mongo import get_db
from app.schemas.template_schema import TemplateUpdate
from app.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("/upload", status_code=201)
async def upload_template(
    template_name: str = Form(...),
    template_description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    record = await TemplateService.upload(db, current_user, template_name, template_description, file)
    return ok(record.model_dump(), message="Template uploaded successfully.")


@router.post("/{template_id}/versions", status_code=201)
async def upload_new_version(
    template_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    record = await TemplateService.upload_new_version(db, current_user, template_id, file)
    return ok(record.model_dump(), message="New template version uploaded successfully.")


@router.get("")
async def list_templates(
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    result = await TemplateService.list_templates(db, search, is_active, page, page_size)
    return ok(result.model_dump())


@router.get("/{template_id}")
async def get_template(
    template_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    record = await TemplateService.get_by_id(db, template_id)
    return ok(record.model_dump())


@router.get("/{template_id}/variables")
async def get_template_variables(
    template_id: str,
    version: Optional[int] = Query(None, description="Specific version; defaults to the current version."),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    result = await TemplateService.get_variables(db, template_id, version)
    return ok(result.model_dump())


@router.put("/{template_id}")
async def update_template(
    template_id: str,
    payload: TemplateUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    record = await TemplateService.update_metadata(db, template_id, payload)
    return ok(record.model_dump(), message="Template updated.")


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    await TemplateService.deactivate(db, template_id)
    return ok(None, message="Template deactivated. Existing affidavits remain unaffected.")
