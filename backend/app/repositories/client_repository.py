from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.queries import client_queries as q

COLLECTION = "clients"


class ClientRepository:

    @staticmethod
    async def create(db: AsyncIOMotorDatabase, doc: dict) -> dict:
        result = await db[COLLECTION].insert_one(doc)
        return await db[COLLECTION].find_one({"_id": result.inserted_id})

    @staticmethod
    async def find_by_id(db: AsyncIOMotorDatabase, client_id: str) -> Optional[dict]:
        try:
            return await db[COLLECTION].find_one(q.by_id(client_id))
        except Exception:
            return None

    @staticmethod
    async def find_list(
        db: AsyncIOMotorDatabase, search: str | None, skip: int, limit: int
    ) -> tuple[list[dict], int]:
        filt = q.search_filter(search)
        cursor = db[COLLECTION].find(filt).sort("_id", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        total = await db[COLLECTION].count_documents(filt)
        return items, total

    @staticmethod
    async def update(db: AsyncIOMotorDatabase, client_id: str, data: dict) -> Optional[dict]:
        await db[COLLECTION].update_one(q.by_id(client_id), q.update_client_document(data))
        return await db[COLLECTION].find_one(q.by_id(client_id))

    @staticmethod
    async def delete(db: AsyncIOMotorDatabase, client_id: str) -> bool:
        result = await db[COLLECTION].delete_one(q.by_id(client_id))
        return result.deleted_count == 1

    @staticmethod
    async def is_referenced_by_affidavits(db: AsyncIOMotorDatabase, client_id: str) -> bool:
        from bson import ObjectId

        count = await db["affidavits"].count_documents({"client_id": ObjectId(client_id)})
        return count > 0
