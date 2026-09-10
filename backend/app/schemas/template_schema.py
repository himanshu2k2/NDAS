from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

VariableType = Literal["text", "number", "date", "textarea", "boolean"]


class TemplateVariable(BaseModel):
    key: str
    label: str
    type: VariableType = "text"
    required: bool = True
    options: Optional[list[str]] = None


class TemplateVersionResponse(BaseModel):
    version: int
    original_file_name: str
    file_type: str
    variables: list[TemplateVariable]
    created_at: datetime


class TemplateResponse(BaseModel):
    id: str
    template_name: str
    template_description: Optional[str] = None
    is_active: bool
    current_version: int
    original_file_name: str
    file_type: str
    variables: list[TemplateVariable]
    created_by: str
    created_at: datetime
    updated_at: datetime


class TemplateVariablesResponse(BaseModel):
    template_id: str
    template_name: str
    version: int
    variables: list[TemplateVariable]


class TemplateUpdate(BaseModel):
    template_name: Optional[str] = Field(None, min_length=2, max_length=200)
    template_description: Optional[str] = None
    is_active: Optional[bool] = None


def current_version_entry(doc: dict) -> dict:
    current = doc["current_version"]
    for entry in doc["versions"]:
        if entry["version"] == current:
            return entry
    return doc["versions"][-1]


def version_entry(doc: dict, version: int) -> Optional[dict]:
    for entry in doc["versions"]:
        if entry["version"] == version:
            return entry
    return None


def to_response(doc: dict) -> TemplateResponse:
    entry = current_version_entry(doc)
    return TemplateResponse(
        id=str(doc["_id"]),
        template_name=doc["template_name"],
        template_description=doc.get("template_description"),
        is_active=doc["is_active"],
        current_version=doc["current_version"],
        original_file_name=entry["original_file_name"],
        file_type=entry["file_type"],
        variables=[TemplateVariable(**v) for v in entry["variables"]],
        created_by=str(doc["created_by"]),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


def to_variables_response(doc: dict, version: Optional[int] = None) -> TemplateVariablesResponse:
    entry = version_entry(doc, version) if version else current_version_entry(doc)
    if entry is None:
        entry = current_version_entry(doc)
    return TemplateVariablesResponse(
        template_id=str(doc["_id"]),
        template_name=doc["template_name"],
        version=entry["version"],
        variables=[TemplateVariable(**v) for v in entry["variables"]],
    )
