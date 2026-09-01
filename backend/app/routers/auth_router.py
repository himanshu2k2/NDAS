from fastapi import APIRouter, Depends

from app.controllers import auth_controller
from app.core.deps import get_current_user
from app.core.responses import ok
from app.schemas.auth_schema import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(payload: RegisterRequest) -> dict:
    user = await auth_controller.register(payload)
    return ok(user, message="User registered successfully.")


@router.post("/login")
async def login(payload: LoginRequest) -> dict:
    data = await auth_controller.login(payload)
    return ok(data)


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)) -> dict:
    await auth_controller.logout(current_user)
    return ok(None, message="Logged out successfully.")


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest) -> dict:
    result = await auth_controller.forgot_password(payload)
    if result is None:
        return ok(None, message="If the account exists, a reset token has been issued.")
    return ok(result, message="Reset token issued.")


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest) -> dict:
    await auth_controller.reset_password(payload)
    return ok(None, message="Password reset successfully.")
