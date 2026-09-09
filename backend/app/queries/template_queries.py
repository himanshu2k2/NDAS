"""Pure MongoDB filter/update-document builders for the `templates` collection.

No I/O happens here — these functions only shape the dicts that the
repository layer hands to motor.

Document shape (one document per template *name*, versions embedded so an
affidavit can always be regenerated/audited against the exact version it
was created from, even after a newer version is uploaded)::

    {
        "_id": ObjectId,
        "template_name": str,
        "template_description": str | None,
        "is_active": bool,
        "current_version": int,
        "versions": [
            {
                "version": int,
                "original_file_name": str,
                "file_path": str,          # relative to storage root
                "file_type": "docx",
                "variables": [ {key, label, type, required, options}, ... ],
                "created_by": ObjectId,
                "created_at": datetime,
            },
            ...
        ],
        "created_by": ObjectId,
        "created_at": datetime,
        "updated_at": datetime,
    }
"""

from datetime import datetime, timezone

from bson import ObjectId


def by_id(template_id: str | ObjectId) -> dict:
    return {"_id": ObjectId(template_id)}


def by_name(template_name: str) -> dict:
    return {"template_name": template_name}


def search_filter(search: str | None, is_active: bool | None) -> dict:
    filt: dict = {}
    if search:
        filt["template_name"] = {"$regex": search, "$options": "i"}
    if is_active is not None:
        filt["is_active"] = is_active
    return filt


def new_template_document(
    template_name: str,
    template_description: str | None,
    original_file_name: str,
    file_path: str,
    variables: list[dict],
    created_by: ObjectId,
) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "template_name": template_name,
        "template_description": template_description,
        "is_active": True,
        "current_version": 1,
        "versions": [
            {
                "version": 1,
                "original_file_name": original_file_name,
                "file_path": file_path,
                "file_type": "docx",
                "variables": variables,
                "created_by": created_by,
                "created_at": now,
            }
        ],
        "created_by": created_by,
        "created_at": now,
        "updated_at": now,
    }


def new_version_entry(
    version: int,
    original_file_name: str,
    file_path: str,
    variables: list[dict],
    created_by: ObjectId,
) -> dict:
    return {
        "version": version,
        "original_file_name": original_file_name,
        "file_path": file_path,
        "file_type": "docx",
        "variables": variables,
        "created_by": created_by,
        "created_at": datetime.now(timezone.utc),
    }


def append_version_update(version_entry: dict) -> dict:
    return {
        "$push": {"versions": version_entry},
        "$set": {
            "current_version": version_entry["version"],
            "updated_at": datetime.now(timezone.utc),
        },
    }


def update_metadata_document(data: dict) -> dict:
    return {"$set": {**data, "updated_at": datetime.now(timezone.utc)}}
