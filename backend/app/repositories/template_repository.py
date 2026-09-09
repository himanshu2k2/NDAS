from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.queries import template_queries as q

COLLECTION = "templates"


class TemplateRepository:

    @staticmethod
    async def create(db: AsyncIOMotorDatabase, doc: dict) -> dict:
        result = await db[COLLECTION].insert_one(doc)
        return await db[COLLECTION].find_one({"_id": result.inserted_id})

    @staticmethod
    async def find_by_id(db: AsyncIOMotorDatabase, template_id: str) -> Optional[dict]:
        try:
            return await db[COLLECTION].find_one(q.by_id(template_id))
        except Exception:
            return None

    @staticmethod
    async def find_by_name(db: AsyncIOMotorDatabase, template_name: str) -> Optional[dict]:
        return await db[COLLECTION].find_one(q.by_name(template_name))

    @staticmethod
    async def find_list(
        db: AsyncIOMotorDatabase,
        search: str | None,
        is_active: bool | None,
        skip: int,
        limit: int,
    ) -> tuple[list[dict], int]:
        filt = q.search_filter(search, is_active)
        cursor = db[COLLECTION].find(filt).sort("_id", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        total = await db[COLLECTION].count_documents(filt)
        return items, total

    @staticmethod
    async def append_version(db: AsyncIOMotorDatabase, template_id: str, version_entry: dict) -> Optional[dict]:
        await db[COLLECTION].update_one(q.by_id(template_id), q.append_version_update(version_entry))
        return await db[COLLECTION].find_one(q.by_id(template_id))

    @staticmethod
    async def update_metadata(db: AsyncIOMotorDatabase, template_id: str, data: dict) -> Optional[dict]:
        await db[COLLECTION].update_one(q.by_id(template_id), q.update_metadata_document(data))
        return await db[COLLECTION].find_one(q.by_id(template_id))

    @staticmethod
    async def deactivate(db: AsyncIOMotorDatabase, template_id: str) -> None:
        await db[COLLECTION].update_one(q.by_id(template_id), q.update_metadata_document({"is_active": False}))

    @staticmethod
    async def is_referenced_by_affidavits(db: AsyncIOMotorDatabase, template_id: str) -> bool:
        count = await db["affidavits"].count_documents({"template_id": ObjectId(template_id)})
        return count > 0
