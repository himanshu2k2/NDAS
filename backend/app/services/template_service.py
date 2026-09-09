from dataclasses import asdict
from io import BytesIO
from typing import Optional

from bson import ObjectId
from fastapi import HTTPException, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.queries.template_queries import new_template_document, new_version_entry
from app.repositories.template_repository import TemplateRepository
from app.schemas.common_schema import Paginated
from app.schemas.template_schema import (
    TemplateResponse,
    TemplateUpdate,
    TemplateVariablesResponse,
    to_response,
    to_variables_response,
)
from app.services.document_service import extract_template_variables
from app.utils.file_handler import (
    delete_storage_file,
    save_template_version,
    validate_template_upload,
)


async def _get_or_404(db: AsyncIOMotorDatabase, template_id: str) -> dict:
    doc = await TemplateRepository.find_by_id(db, template_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found.")
    return doc


def _variable_dicts(source: BytesIO) -> list[dict]:
    variables = extract_template_variables(source)
    if not variables:
        raise HTTPException(
            status_code=400,
            detail="No {{variable}} placeholders were found in this document. "
            "Uploaded templates must use the {{variable_name}} convention.",
        )
    return [asdict(v) for v in variables]


class TemplateService:

    @staticmethod
    async def upload(
        db: AsyncIOMotorDatabase,
        current_user: dict,
        template_name: str,
        template_description: Optional[str],
        file: UploadFile,
    ) -> TemplateResponse:
        if await TemplateRepository.find_by_name(db, template_name):
            raise HTTPException(status_code=409, detail=f"A template named '{template_name}' already exists.")

        content = await file.read()
        validate_template_upload(file, content)
        variables = _variable_dicts(BytesIO(content))

        template_id = ObjectId()
        file_path = save_template_version(str(template_id), 1, content)
        doc = new_template_document(
            template_name=template_name,
            template_description=template_description,
            original_file_name=file.filename,
            file_path=file_path,
            variables=variables,
            created_by=current_user["_id"],
        )
        doc["_id"] = template_id

        try:
            created = await TemplateRepository.create(db, doc)
        except Exception:
            delete_storage_file(file_path)
            raise
        return to_response(created)

    @staticmethod
    async def upload_new_version(
        db: AsyncIOMotorDatabase, current_user: dict, template_id: str, file: UploadFile
    ) -> TemplateResponse:
        template = await _get_or_404(db, template_id)
        content = await file.read()
        validate_template_upload(file, content)
        variables = _variable_dicts(BytesIO(content))

        next_version = template["current_version"] + 1
        file_path = save_template_version(template_id, next_version, content)
        entry = new_version_entry(
            version=next_version,
            original_file_name=file.filename,
            file_path=file_path,
            variables=variables,
            created_by=current_user["_id"],
        )

        try:
            updated = await TemplateRepository.append_version(db, template_id, entry)
        except Exception:
            delete_storage_file(file_path)
            raise
        return to_response(updated)

    @staticmethod
    async def get_by_id(db: AsyncIOMotorDatabase, template_id: str) -> TemplateResponse:
        doc = await _get_or_404(db, template_id)
        return to_response(doc)

    @staticmethod
    async def get_variables(
        db: AsyncIOMotorDatabase, template_id: str, version: Optional[int] = None
    ) -> TemplateVariablesResponse:
        doc = await _get_or_404(db, template_id)
        return to_variables_response(doc, version)

    @staticmethod
    async def list_templates(
        db: AsyncIOMotorDatabase,
        search: Optional[str],
        is_active: Optional[bool],
        page: int,
        page_size: int,
    ) -> Paginated[TemplateResponse]:
        skip = (page - 1) * page_size
        items, total = await TemplateRepository.find_list(db, search, is_active, skip, page_size)
        return Paginated[TemplateResponse](
            total=total, page=page, page_size=page_size, items=[to_response(d) for d in items]
        )

    @staticmethod
    async def update_metadata(
        db: AsyncIOMotorDatabase, template_id: str, payload: TemplateUpdate
    ) -> TemplateResponse:
        await _get_or_404(db, template_id)
        data = payload.model_dump(exclude_none=True)
        if not data:
            raise HTTPException(status_code=400, detail="No fields provided to update.")
        if "template_name" in data:
            existing = await TemplateRepository.find_by_name(db, data["template_name"])
            if existing and str(existing["_id"]) != template_id:
                raise HTTPException(
                    status_code=409, detail=f"A template named '{data['template_name']}' already exists."
                )
        updated = await TemplateRepository.update_metadata(db, template_id, data)
        return to_response(updated)

    @staticmethod
    async def deactivate(db: AsyncIOMotorDatabase, template_id: str) -> None:
        await _get_or_404(db, template_id)
        # Templates are never hard-deleted: affidavits generated from any
        # version must remain auditable even after the template is retired.
        await TemplateRepository.deactivate(db, template_id)
