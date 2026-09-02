from typing import Literal

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    fullName: str
    username: str
    email: str
    password: str = Field(min_length=6)
    mobile: str
    role: Literal["admin", "junior"] = "junior"


class LoginRequest(BaseModel):
    identifier: str
    password: str


class ForgotPasswordRequest(BaseModel):
    identifier: str


class ResetPasswordRequest(BaseModel):
    token: str
    newPassword: str = Field(min_length=6)
    confirmPassword: str


def to_public_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "fullName": user["fullName"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
    }
