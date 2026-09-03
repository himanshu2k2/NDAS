from bson import ObjectId


def by_id(affidavit_id: str) -> dict:
    return {"_id": ObjectId(affidavit_id)}


def search_filter(search: str | None) -> dict:
    if not search:
        return {}
    pattern = {"$regex": search, "$options": "i"}
    return {"$or": [{"donor_name": pattern}, {"recipient_name": pattern}, {"hospital_name": pattern}]}


def new_affidavit_document(data: dict) -> dict:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    return {**data, "created_at": now, "updated_at": now}


def update_affidavit_document(data: dict) -> dict:
    from datetime import datetime, timezone
    return {"$set": {**data, "updated_at": datetime.now(timezone.utc)}}
