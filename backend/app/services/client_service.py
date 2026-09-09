from typing import Optional

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.queries.client_queries import new_client_document
from app.repositories.client_repository import ClientRepository
from app.schemas.client_schema import ClientCreate, ClientResponse, ClientUpdate, to_response
from app.schemas.common_schema import Paginated


async def _get_or_404(db: AsyncIOMotorDatabase, client_id: str) -> dict:
    doc = await ClientRepository.find_by_id(db, client_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found.")
    return doc


class ClientService:

    @staticmethod
    async def create(db: AsyncIOMotorDatabase, current_user: dict, payload: ClientCreate) -> ClientResponse:
        doc = new_client_document(
            name=payload.name,
            mobile=payload.mobile,
            aadhar_no=payload.aadhar_no,
            email=payload.email,
            address=payload.address,
            created_by=current_user["_id"],
        )
        created = await ClientRepository.create(db, doc)
        return to_response(created)

    @staticmethod
    async def get_by_id(db: AsyncIOMotorDatabase, client_id: str) -> ClientResponse:
        doc = await _get_or_404(db, client_id)
        return to_response(doc)

    @staticmethod
    async def list_clients(
        db: AsyncIOMotorDatabase, search: Optional[str], page: int, page_size: int
    ) -> Paginated[ClientResponse]:
        skip = (page - 1) * page_size
        items, total = await ClientRepository.find_list(db, search, skip, page_size)
        return Paginated[ClientResponse](
            total=total, page=page, page_size=page_size, items=[to_response(d) for d in items]
        )

    @staticmethod
    async def update(db: AsyncIOMotorDatabase, client_id: str, payload: ClientUpdate) -> ClientResponse:
        await _get_or_404(db, client_id)
        data = payload.model_dump(exclude_none=True)
        if not data:
            raise HTTPException(status_code=400, detail="No fields provided to update.")
        updated = await ClientRepository.update(db, client_id, data)
        return to_response(updated)

    @staticmethod
    async def delete(db: AsyncIOMotorDatabase, client_id: str) -> None:
        await _get_or_404(db, client_id)
        if await ClientRepository.is_referenced_by_affidavits(db, client_id):
            raise HTTPException(
                status_code=409,
                detail="This client has existing affidavits and cannot be deleted.",
            )
        await ClientRepository.delete(db, client_id)
