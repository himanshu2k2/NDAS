import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.core.security import hash_password
from app.db.mongo import get_db
from app.queries import user_queries as q

RESET_TOKEN_TTL_MINUTES = 30


class UserRepository:
    """Data-access layer for the `users` collection."""

    @staticmethod
    async def find_by_identifier(identifier: str) -> Optional[dict]:
        return await get_db().users.find_one(q.by_identifier(identifier))

    @staticmethod
    async def find_by_username_or_email(username: str, email: str) -> Optional[dict]:
        return await get_db().users.find_one(q.by_username_or_email(username, email))

    @staticmethod
    async def find_by_id(user_id: ObjectId) -> Optional[dict]:
        return await get_db().users.find_one(q.by_id(user_id))

    @staticmethod
    async def find_by_reset_token(token: str) -> Optional[dict]:
        return await get_db().users.find_one(q.by_reset_token(token))

    @staticmethod
    async def create(
        full_name: str, username: str, email: str, password: str, mobile: str, role: str
    ) -> dict:
        document = q.new_user_document(full_name, username, email, hash_password(password), mobile, role)
        try:
            result = await get_db().users.insert_one(document)
        except DuplicateKeyError as exc:
            raise ValueError("Username or email already registered.") from exc
        return await UserRepository.find_by_id(result.inserted_id)

    @staticmethod
    async def set_reset_token(user_id: ObjectId) -> tuple[str, int]:
        token = secrets.token_urlsafe(32)
        expiry = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)
        await get_db().users.update_one(q.by_id(user_id), q.set_reset_token_update(token, expiry))
        return token, RESET_TOKEN_TTL_MINUTES

    @staticmethod
    def reset_token_is_valid(user: dict) -> bool:
        expiry = user.get("resetTokenExpiry")
        if expiry is not None and expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return bool(expiry) and expiry >= datetime.now(timezone.utc)

    @staticmethod
    async def update_password(user_id: ObjectId, new_password: str) -> None:
        await get_db().users.update_one(
            q.by_id(user_id), q.update_password_update(hash_password(new_password))
        )
