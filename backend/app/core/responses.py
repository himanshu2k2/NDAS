from typing import Any, Optional


def ok(data: Any = None, message: Optional[str] = None, meta: Optional[dict] = None) -> dict:
    body: dict[str, Any] = {"success": True, "data": data}
    if message is not None:
        body["message"] = message
    if meta is not None:
        body["meta"] = meta
    return body


def fail(message: str, data: Any = None) -> dict:
    return {"success": False, "data": data, "message": message}