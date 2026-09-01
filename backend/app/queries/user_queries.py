from datetime import datetime, timezone

from bson import ObjectId

"""Pure MongoDB filter/update-document builders for the `users` collection.

No I/O happens here — these functions only shape the dicts that the
repository layer hands to motor/pymongo.
"""


def by_id(user_id: ObjectId) -> dict:
    return {"_id": user_id}


def by_identifier(identifier: str) -> dict:
    return {"$or": [{"username": identifier}, {"email": identifier}]}


def by_username_or_email(username: str, email: str) -> dict:
    return {"$or": [{"username": username}, {"email": email}]}


def by_reset_token(token: str) -> dict:
    return {"resetToken": token}


def new_user_document(
    full_name: str,
    username: str,
    email: str,
    password_hash: str,
    mobile: str,
    role: str,
) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "fullName": full_name,
        "username": username,
        "email": email,
        "passwordHash": password_hash,
        "mobile": mobile,
        "role": role,
        "status": True,
        "createdAt": now,
        "updatedAt": now,
    }


def set_reset_token_update(token: str, expiry: datetime) -> dict:
    return {"$set": {"resetToken": token, "resetTokenExpiry": expiry}}


def update_password_update(password_hash: str) -> dict:
    return {
        "$set": {"passwordHash": password_hash, "updatedAt": datetime.now(timezone.utc)},
        "$unset": {"resetToken": "", "resetTokenExpiry": ""},
    }
