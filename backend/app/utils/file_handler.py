"""Filesystem helpers for template originals and generated affidavits.

Originals live under ``storage/templates/<template_id>/v<version>/`` and are
never overwritten. Generated affidavits live under
``storage/generated/<affidavit_id>.docx``. All on-disk filenames are
generated server-side (uuid-based); the caller's original filename is kept
only as metadata.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings

ALLOWED_TEMPLATE_EXTENSION = ".docx"
ALLOWED_TEMPLATE_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream",  # some browsers/clients omit the specific type
}
MAX_TEMPLATE_SIZE_BYTES = settings.max_template_upload_mb * 1024 * 1024


def validate_template_upload(file: UploadFile, content: bytes) -> None:
    if not file.filename or not file.filename.lower().endswith(ALLOWED_TEMPLATE_EXTENSION):
        raise HTTPException(status_code=400, detail="Only .docx files are supported.")

    if file.content_type and file.content_type not in ALLOWED_TEMPLATE_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid Word (.docx) document.")

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > MAX_TEMPLATE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Template file exceeds the {settings.max_template_upload_mb}MB size limit.",
        )

    # A .docx is a zip archive — reject anything that isn't, before python-docx touches it.
    if content[:2] != b"PK":
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid .docx document.")


def _templates_root() -> Path:
    return settings.storage_path / "templates"


def _generated_root() -> Path:
    return settings.storage_path / "generated"


def save_template_version(template_id: str, version: int, content: bytes) -> str:
    """Persist an uploaded template version and return its path relative to storage root."""
    directory = _templates_root() / template_id / f"v{version}"
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.docx"
    absolute_path = directory / filename
    absolute_path.write_bytes(content)
    return str((Path("templates") / template_id / f"v{version}" / filename).as_posix())


def save_generated_affidavit(affidavit_id: str, content: bytes) -> str:
    """Persist a generated affidavit and return its path relative to storage root."""
    directory = _generated_root()
    directory.mkdir(parents=True, exist_ok=True)
    absolute_path = directory / f"{affidavit_id}.docx"
    absolute_path.write_bytes(content)
    return str((Path("generated") / f"{affidavit_id}.docx").as_posix())


def resolve_storage_path(relative_path: str) -> Path:
    return settings.storage_path / relative_path


def delete_storage_file(relative_path: str | None) -> None:
    if not relative_path:
        return
    path = resolve_storage_path(relative_path)
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
