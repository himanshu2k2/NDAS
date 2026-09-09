import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email(v: Optional[str]) -> Optional[str]:
    if v is not None and not _EMAIL_PATTERN.match(v):
        raise ValueError("Invalid email address.")
    return v


class ClientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    mobile: str = Field(min_length=10, max_length=15)
    aadhar_no: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    address: Optional[str] = None

    @field_validator("mobile")
    @classmethod
    def mobile_must_be_digits(cls, v: str) -> str:
        if not v.replace("+", "").replace(" ", "").isdigit():
            raise ValueError("Mobile number must contain only digits.")
        return v

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: Optional[str]) -> Optional[str]:
        return _validate_email(v)


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    mobile: Optional[str] = Field(None, min_length=10, max_length=15)
    aadhar_no: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    address: Optional[str] = None

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: Optional[str]) -> Optional[str]:
        return _validate_email(v)


class ClientResponse(BaseModel):
    id: str
    name: str
    mobile: str
    aadhar_no: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime
    updated_at: datetime


def to_response(doc: dict) -> ClientResponse:
    return ClientResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        mobile=doc["mobile"],
        aadhar_no=doc.get("aadhar_no"),
        email=doc.get("email"),
        address=doc.get("address"),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )
