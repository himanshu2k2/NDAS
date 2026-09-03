from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class KidneyAffidavitBase(BaseModel):
    donor_name: str = Field(min_length=2, max_length=200)
    donor_age: int = Field(ge=18, le=65)
    donor_address: str = Field(min_length=5)
    donor_relationship: str = Field(min_length=2, max_length=100)
    donor_id_type: str = Field(min_length=2, max_length=100)
    donor_id_number: str = Field(min_length=2, max_length=100)

    recipient_name: str = Field(min_length=2, max_length=200)
    recipient_age: int = Field(ge=1, le=120)
    recipient_address: str = Field(min_length=5)
    recipient_id_type: str = Field(min_length=2, max_length=100)
    recipient_id_number: str = Field(min_length=2, max_length=100)

    hospital_name: str = Field(min_length=2, max_length=300)
    hospital_address: str = Field(min_length=5)
    doctor_name: str = Field(min_length=2, max_length=200)
    doctor_registration_no: str = Field(min_length=2, max_length=100)
    transplant_date: date

    donor_consent: bool = True
    relationship_proof: str = Field(min_length=2, max_length=300)

    place: str = Field(min_length=2, max_length=200)
    affidavit_date: date

    @field_validator("donor_consent")
    @classmethod
    def consent_must_be_true(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Donor consent must be True to proceed.")
        return v


class KidneyAffidavitCreate(KidneyAffidavitBase):
    pass


class KidneyAffidavitUpdate(BaseModel):
    donor_name: Optional[str] = Field(None, min_length=2, max_length=200)
    donor_age: Optional[int] = Field(None, ge=18, le=65)
    donor_address: Optional[str] = None
    donor_relationship: Optional[str] = Field(None, max_length=100)
    donor_id_type: Optional[str] = Field(None, max_length=100)
    donor_id_number: Optional[str] = Field(None, max_length=100)

    recipient_name: Optional[str] = Field(None, min_length=2, max_length=200)
    recipient_age: Optional[int] = Field(None, ge=1, le=120)
    recipient_address: Optional[str] = None
    recipient_id_type: Optional[str] = Field(None, max_length=100)
    recipient_id_number: Optional[str] = Field(None, max_length=100)

    hospital_name: Optional[str] = Field(None, max_length=300)
    hospital_address: Optional[str] = None
    doctor_name: Optional[str] = Field(None, max_length=200)
    doctor_registration_no: Optional[str] = Field(None, max_length=100)
    transplant_date: Optional[date] = None

    donor_consent: Optional[bool] = None
    relationship_proof: Optional[str] = Field(None, max_length=300)

    place: Optional[str] = Field(None, max_length=200)
    affidavit_date: Optional[date] = None


class KidneyAffidavitResponse(KidneyAffidavitBase):
    id: str
    created_at: datetime
    updated_at: datetime


class PaginatedAffidavits(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[KidneyAffidavitResponse]


def to_response(doc: dict) -> KidneyAffidavitResponse:
    return KidneyAffidavitResponse(
        id=str(doc["_id"]),
        **{k: v for k, v in doc.items() if k != "_id"},
    )
