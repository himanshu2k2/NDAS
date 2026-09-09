from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.queries import affidavit_queries as q

COLLECTION = "affidavits"


class AffidavitRepository:

    @staticmethod
    async def create(db: AsyncIOMotorDatabase, doc: dict) -> dict:
        result = await db[COLLECTION].insert_one(doc)
        return await db[COLLECTION].find_one({"_id": result.inserted_id})

    @staticmethod
    async def find_by_id(db: AsyncIOMotorDatabase, affidavit_id: str) -> Optional[dict]:
        try:
            return await db[COLLECTION].find_one(q.by_id(affidavit_id))
        except Exception:
            return None

    @staticmethod
    async def find_list(
        db: AsyncIOMotorDatabase,
        search: str | None,
        client_id: str | None,
        template_id: str | None,
        status: str | None,
        skip: int,
        limit: int,
    ) -> tuple[list[dict], int]:
        filt = q.search_filter(search, client_id, template_id, status)
        cursor = db[COLLECTION].find(filt).sort("_id", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        total = await db[COLLECTION].count_documents(filt)
        return items, total

    @staticmethod
    async def delete(db: AsyncIOMotorDatabase, affidavit_id: str) -> bool:
        result = await db[COLLECTION].delete_one(q.by_id(affidavit_id))
        return result.deleted_count == 1
