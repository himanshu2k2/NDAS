"""Pure MongoDB filter/update-document builders for the `clients` collection.

No I/O happens here — these functions only shape the dicts that the
repository layer hands to motor.
"""

from datetime import datetime, timezone

from bson import ObjectId


def by_id(client_id: str | ObjectId) -> dict:
    return {"_id": ObjectId(client_id)}


def search_filter(search: str | None) -> dict:
    if not search:
        return {}
    pattern = {"$regex": search, "$options": "i"}
    return {"$or": [{"name": pattern}, {"mobile": pattern}, {"aadhar_no": pattern}, {"email": pattern}]}


def new_client_document(
    name: str,
    mobile: str,
    aadhar_no: str | None,
    email: str | None,
    address: str | None,
    created_by: ObjectId,
) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "name": name,
        "mobile": mobile,
        "aadhar_no": aadhar_no,
        "email": email,
        "address": address,
        "created_by": created_by,
        "created_at": now,
        "updated_at": now,
    }


def update_client_document(data: dict) -> dict:
    return {"$set": {**data, "updated_at": datetime.now(timezone.utc)}}
