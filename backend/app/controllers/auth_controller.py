from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import HTTPException

from app.core.security import create_access_token, verify_password
from app.db.mongo import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    to_public_user,
)


async def _log_activity(user_id: ObjectId, action: str) -> None:
    await get_db().activity_logs.insert_one(
        {
            "userId": user_id,
            "action": action,
            "module": "auth",
            "timestamp": datetime.now(timezone.utc),
        }
    )


async def register(payload: RegisterRequest) -> dict:
    existing = await UserRepository.find_by_username_or_email(payload.username, payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Username or email already registered.")

    try:
        user = await UserRepository.create(
            payload.fullName, payload.username, payload.email, payload.password, payload.mobile, payload.role
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return to_public_user(user)


async def login(payload: LoginRequest) -> dict:
    user = await UserRepository.find_by_identifier(payload.identifier)
    if not user or not user.get("status") or not verify_password(payload.password, user["passwordHash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token, expires_in = create_access_token(str(user["_id"]), user["role"])
    await _log_activity(user["_id"], "login")

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": to_public_user(user),
    }


async def logout(current_user: dict) -> None:
    await _log_activity(current_user["_id"], "logout")


async def forgot_password(payload: ForgotPasswordRequest) -> Optional[dict]:
    user = await UserRepository.find_by_identifier(payload.identifier)
    if not user:
        return None

    token, ttl_minutes = await UserRepository.set_reset_token(user["_id"])
    # No email service is wired up yet, so the token is returned directly for testing.
    return {"resetToken": token, "expiresInMinutes": ttl_minutes}


async def reset_password(payload: ResetPasswordRequest) -> None:
    if payload.newPassword != payload.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    user = await UserRepository.find_by_reset_token(payload.token)
    if not user or not UserRepository.reset_token_is_valid(user):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    await UserRepository.update_password(user["_id"], payload.newPassword)
