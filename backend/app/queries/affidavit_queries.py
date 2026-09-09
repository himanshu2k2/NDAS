"""Pure MongoDB filter/update-document builders for the `affidavits` collection.

No I/O happens here — these functions only shape the dicts that the
repository layer hands to motor.
"""

from datetime import datetime, timezone

from bson import ObjectId


def by_id(affidavit_id: str | ObjectId) -> dict:
    return {"_id": ObjectId(affidavit_id)}


def search_filter(
    search: str | None,
    client_id: str | None,
    template_id: str | None,
    status: str | None,
) -> dict:
    filt: dict = {}
    if search:
        pattern = {"$regex": search, "$options": "i"}
        filt["$or"] = [{"affidavit_name": pattern}, {"client_name": pattern}, {"mobile": pattern}]
    if client_id:
        filt["client_id"] = ObjectId(client_id)
    if template_id:
        filt["template_id"] = ObjectId(template_id)
    if status:
        filt["status"] = status
    return filt


def new_affidavit_document(
    client: dict,
    template_id: ObjectId,
    template_version: int,
    template_name: str,
    affidavit_name: str,
    issue_date: str,
    variable_data: dict,
    generated_file_path: str,
    created_by: ObjectId,
) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "client_id": client["_id"],
        "template_id": template_id,
        "template_version": template_version,
        "template_name": template_name,
        "affidavit_name": affidavit_name,
        "client_name": client["name"],
        "mobile": client["mobile"],
        "aadhar_no": client.get("aadhar_no"),
        "issue_date": issue_date,
        "variable_data": variable_data,
        "generated_file_path": generated_file_path,
        "status": "generated",
        "created_by": created_by,
        "created_at": now,
        "updated_at": now,
    }
