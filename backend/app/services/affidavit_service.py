from typing import Any, Optional

from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.queries.affidavit_queries import new_affidavit_document
from app.repositories.affidavit_repository import AffidavitRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.template_repository import TemplateRepository
from app.schemas.affidavit_schema import AffidavitCreate, AffidavitResponse, to_response
from app.schemas.common_schema import Paginated
from app.schemas.template_schema import current_version_entry
from app.services.document_service import generate_affidavit_docx
from app.utils.file_handler import delete_storage_file, resolve_storage_path, save_generated_affidavit


def _validate_and_coerce_variables(variable_specs: list[dict], submitted: dict[str, Any]) -> dict[str, Any]:
    known_keys = {spec["key"] for spec in variable_specs}
    unexpected = sorted(set(submitted.keys()) - known_keys)
    if unexpected:
        raise HTTPException(
            status_code=400,
            detail=f"Unexpected variable(s) not defined on this template: {', '.join(unexpected)}",
        )

    missing = [
        spec["key"]
        for spec in variable_specs
        if spec["required"] and (submitted.get(spec["key"]) in (None, ""))
    ]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required variable(s): {', '.join(missing)}",
        )

    coerced: dict[str, Any] = {}
    for spec in variable_specs:
        key = spec["key"]
        value = submitted.get(key)
        if value in (None, ""):
            coerced[key] = ""
            continue

        vtype = spec["type"]
        if vtype == "number":
            try:
                number = float(value)
            except (TypeError, ValueError):
                raise HTTPException(status_code=422, detail=f"Variable '{key}' must be a number.")
            coerced[key] = int(number) if number.is_integer() else number
        elif vtype == "boolean":
            if isinstance(value, bool):
                coerced[key] = value
            elif str(value).strip().lower() in ("true", "1", "yes"):
                coerced[key] = True
            elif str(value).strip().lower() in ("false", "0", "no"):
                coerced[key] = False
            else:
                raise HTTPException(status_code=422, detail=f"Variable '{key}' must be a boolean.")
        else:
            coerced[key] = str(value)

    return coerced


async def _get_client_or_404(db: AsyncIOMotorDatabase, client_id: str) -> dict:
    client = await ClientRepository.find_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found.")
    return client


async def _get_active_template_or_404(db: AsyncIOMotorDatabase, template_id: str) -> dict:
    template = await TemplateRepository.find_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found.")
    if not template["is_active"]:
        raise HTTPException(status_code=400, detail="This template is inactive and cannot be used.")
    return template


async def _get_affidavit_or_404(db: AsyncIOMotorDatabase, affidavit_id: str) -> dict:
    doc = await AffidavitRepository.find_by_id(db, affidavit_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Affidavit {affidavit_id} not found.")
    return doc


class AffidavitService:

    @staticmethod
    async def create(db: AsyncIOMotorDatabase, current_user: dict, payload: AffidavitCreate) -> AffidavitResponse:
        client = await _get_client_or_404(db, payload.client_id)
        template = await _get_active_template_or_404(db, payload.template_id)

        version_doc = current_version_entry(template)
        variable_data = _validate_and_coerce_variables(version_doc["variables"], payload.variables)

        template_path = resolve_storage_path(version_doc["file_path"])
        buffer = generate_affidavit_docx(template_path, variable_data)

        affidavit_id = ObjectId()
        generated_file_path = save_generated_affidavit(str(affidavit_id), buffer.getvalue())

        doc = new_affidavit_document(
            client=client,
            template_id=template["_id"],
            template_version=version_doc["version"],
            template_name=template["template_name"],
            affidavit_name=payload.affidavit_name or template["template_name"],
            issue_date=str(payload.issue_date),
            variable_data=variable_data,
            generated_file_path=generated_file_path,
            created_by=current_user["_id"],
        )
        doc["_id"] = affidavit_id

        try:
            created = await AffidavitRepository.create(db, doc)
        except Exception as exc:
            delete_storage_file(generated_file_path)
            raise HTTPException(status_code=500, detail="Failed to save the affidavit record.") from exc

        return to_response(created)

    @staticmethod
    async def get_by_id(db: AsyncIOMotorDatabase, affidavit_id: str) -> AffidavitResponse:
        doc = await _get_affidavit_or_404(db, affidavit_id)
        return to_response(doc)

    @staticmethod
    async def get_download_info(db: AsyncIOMotorDatabase, affidavit_id: str) -> tuple[str, str]:
        doc = await _get_affidavit_or_404(db, affidavit_id)
        path = resolve_storage_path(doc["generated_file_path"])
        if not path.exists():
            raise HTTPException(status_code=404, detail="Generated affidavit file is missing from storage.")
        filename = f"{doc['affidavit_name']}.docx".replace("/", "_").replace("\\", "_")
        return str(path), filename

    @staticmethod
    async def list_affidavits(
        db: AsyncIOMotorDatabase,
        search: Optional[str],
        client_id: Optional[str],
        template_id: Optional[str],
        status: Optional[str],
        page: int,
        page_size: int,
    ) -> Paginated[AffidavitResponse]:
        skip = (page - 1) * page_size
        items, total = await AffidavitRepository.find_list(
            db, search, client_id, template_id, status, skip, page_size
        )
        return Paginated[AffidavitResponse](
            total=total, page=page, page_size=page_size, items=[to_response(d) for d in items]
        )

    @staticmethod
    async def delete(db: AsyncIOMotorDatabase, affidavit_id: str) -> None:
        doc = await _get_affidavit_or_404(db, affidavit_id)
        await AffidavitRepository.delete(db, affidavit_id)
        delete_storage_file(doc["generated_file_path"])
