from io import BytesIO

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.document.docx_generator import generate_docx
from app.document.pdf_generator import generate_pdf
from app.repositories.kidney_affidavit_repository import KidneyAffidavitRepository
from app.schemas.kidney_affidavit_schema import (
    KidneyAffidavitCreate,
    KidneyAffidavitUpdate,
    PaginatedAffidavits,
    KidneyAffidavitResponse,
    to_response,
)
from app.templates.kidney_affidavit_template import AffidavitContext


async def _get_or_404(db: AsyncIOMotorDatabase, affidavit_id: str) -> dict:
    doc = await KidneyAffidavitRepository.find_by_id(db, affidavit_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Affidavit {affidavit_id} not found.")
    return doc


def _to_context(doc: dict) -> AffidavitContext:
    return AffidavitContext(
        donor_name=doc["donor_name"],
        donor_age=doc["donor_age"],
        donor_address=doc["donor_address"],
        donor_relationship=doc["donor_relationship"],
        donor_id_type=doc["donor_id_type"],
        donor_id_number=doc["donor_id_number"],
        recipient_name=doc["recipient_name"],
        recipient_age=doc["recipient_age"],
        recipient_address=doc["recipient_address"],
        recipient_id_type=doc["recipient_id_type"],
        recipient_id_number=doc["recipient_id_number"],
        hospital_name=doc["hospital_name"],
        hospital_address=doc["hospital_address"],
        doctor_name=doc["doctor_name"],
        doctor_registration_no=doc["doctor_registration_no"],
        transplant_date=str(doc["transplant_date"]),
        donor_consent=doc["donor_consent"],
        relationship_proof=doc["relationship_proof"],
        place=doc["place"],
        affidavit_date=str(doc["affidavit_date"]),
    )


class KidneyAffidavitService:

    @staticmethod
    async def create(db: AsyncIOMotorDatabase, payload: KidneyAffidavitCreate) -> KidneyAffidavitResponse:
        data = payload.model_dump()
        # convert date → string for MongoDB storage
        data["transplant_date"] = str(data["transplant_date"])
        data["affidavit_date"] = str(data["affidavit_date"])
        doc = await KidneyAffidavitRepository.create(db, data)
        return to_response(doc)

    @staticmethod
    async def get_by_id(db: AsyncIOMotorDatabase, affidavit_id: str) -> KidneyAffidavitResponse:
        doc = await _get_or_404(db, affidavit_id)
        return to_response(doc)

    @staticmethod
    async def list_affidavits(
        db: AsyncIOMotorDatabase, search: str | None, page: int, page_size: int
    ) -> PaginatedAffidavits:
        skip = (page - 1) * page_size
        items, total = await KidneyAffidavitRepository.find_list(db, search, skip, page_size)
        return PaginatedAffidavits(
            total=total,
            page=page,
            page_size=page_size,
            items=[to_response(d) for d in items],
        )

    @staticmethod
    async def update(
        db: AsyncIOMotorDatabase, affidavit_id: str, payload: KidneyAffidavitUpdate
    ) -> KidneyAffidavitResponse:
        await _get_or_404(db, affidavit_id)
        data = payload.model_dump(exclude_none=True)
        if "transplant_date" in data:
            data["transplant_date"] = str(data["transplant_date"])
        if "affidavit_date" in data:
            data["affidavit_date"] = str(data["affidavit_date"])
        doc = await KidneyAffidavitRepository.update(db, affidavit_id, data)
        return to_response(doc)

    @staticmethod
    async def delete(db: AsyncIOMotorDatabase, affidavit_id: str) -> None:
        await _get_or_404(db, affidavit_id)
        await KidneyAffidavitRepository.delete(db, affidavit_id)

    @staticmethod
    async def generate_docx(db: AsyncIOMotorDatabase, affidavit_id: str) -> BytesIO:
        doc = await _get_or_404(db, affidavit_id)
        return generate_docx(_to_context(doc))

    @staticmethod
    async def generate_pdf(db: AsyncIOMotorDatabase, affidavit_id: str) -> BytesIO:
        doc = await _get_or_404(db, affidavit_id)
        return generate_pdf(_to_context(doc))
