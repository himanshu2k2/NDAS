from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AffidavitCreate(BaseModel):
    client_id: str
    template_id: str
    affidavit_name: Optional[str] = None
    issue_date: date
    variables: dict[str, Any] = Field(default_factory=dict)


class AffidavitResponse(BaseModel):
    id: str
    client_id: str
    template_id: str
    template_version: int
    template_name: str
    affidavit_name: str
    client_name: str
    mobile: str
    aadhar_no: Optional[str] = None
    issue_date: str
    variable_data: dict[str, Any]
    generated_file_path: str
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime


def to_response(doc: dict) -> AffidavitResponse:
    return AffidavitResponse(
        id=str(doc["_id"]),
        client_id=str(doc["client_id"]),
        template_id=str(doc["template_id"]),
        template_version=doc["template_version"],
        template_name=doc["template_name"],
        affidavit_name=doc["affidavit_name"],
        client_name=doc["client_name"],
        mobile=doc["mobile"],
        aadhar_no=doc.get("aadhar_no"),
        issue_date=doc["issue_date"],
        variable_data=doc["variable_data"],
        generated_file_path=doc["generated_file_path"],
        status=doc["status"],
        created_by=str(doc["created_by"]),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )
