from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.security import decode_access_token
from app.db.mongo import get_db

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = ObjectId(payload.get("sub"))
    except (JWTError, InvalidId, TypeError):
        raise HTTPException(status_code=401, detail="Please login again.")

    user = await get_db().users.find_one({"_id": user_id})
    if not user or not user.get("status"):
        raise HTTPException(status_code=401, detail="Please login again.")
    return user
