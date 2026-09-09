"""Initialize NDAOMS MongoDB: collections, indexes, and admin user."""

from __future__ import annotations

import os
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

import bcrypt
import certifi
from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, TEXT, MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Prefer IPv4. Some Windows/ISP setups return NAT64 IPv6 for Atlas hosts and
# TLS then fails with TLSV1_ALERT_INTERNAL_ERROR.
_orig_getaddrinfo = socket.getaddrinfo


def _getaddrinfo_ipv4_first(host, port, family=0, type=0, proto=0, flags=0):
    infos = _orig_getaddrinfo(host, port, family, type, proto, flags)
    ipv4 = [i for i in infos if i[0] == socket.AF_INET]
    return ipv4 or infos


socket.getaddrinfo = _getaddrinfo_ipv4_first

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "ndaoms")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@office.local")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ChangeMe123!")
ADMIN_FULL_NAME = os.getenv("ADMIN_FULL_NAME", "Senior Advocate")
ADMIN_MOBILE = os.getenv("ADMIN_MOBILE", "9999999999")


def _redacted_uri(uri: str) -> str:
    """Hide credentials when printing connection info."""
    if "://" not in uri:
        return uri
    scheme, rest = uri.split("://", 1)
    if "@" not in rest:
        return uri
    _, host = rest.rsplit("@", 1)
    return f"{scheme}://***:***@{host}"


def _mongo_client(uri: str) -> MongoClient:
    kwargs: dict = {"serverSelectionTimeoutMS": 20000}
    if uri.startswith("mongodb+srv://") or "tls=true" in uri.lower():
        kwargs["tlsCAFile"] = certifi.where()
    return MongoClient(uri, **kwargs)

COLLECTIONS = [
    "users",
    "clients",
    "templates",
    "affidavits",
    "documents",
    "assignments",
    "activity_logs",
]


def ensure_collections(db) -> None:
    existing = set(db.list_collection_names())
    for name in COLLECTIONS:
        if name not in existing:
            db.create_collection(name)
            print(f"Created collection: {name}")
        else:
            print(f"Collection exists: {name}")


def ensure_indexes(db) -> None:
    db.users.create_index("username", unique=True)
    db.users.create_index("email", unique=True)
    db.users.create_index([("role", ASCENDING), ("status", ASCENDING)])

    db.clients.create_index("mobile")
    db.clients.create_index("aadhar_no", sparse=True)
    db.clients.create_index([("name", TEXT)])

    db.templates.create_index("template_name", unique=True)
    db.templates.create_index("is_active")

    db.affidavits.create_index([("client_id", ASCENDING), ("created_at", DESCENDING)])
    db.affidavits.create_index([("template_id", ASCENDING), ("created_at", DESCENDING)])
    db.affidavits.create_index("status")

    db.documents.create_index("documentCode", unique=True)
    db.documents.create_index([("clientId", ASCENDING), ("generatedAt", DESCENDING)])
    db.documents.create_index([("documentType", ASCENDING), ("generatedAt", DESCENDING)])
    db.documents.create_index("generatedBy")

    db.assignments.create_index("assignmentCode", unique=True)
    db.assignments.create_index([("assignedTo", ASCENDING), ("status", ASCENDING)])
    db.assignments.create_index("clientId")

    db.activity_logs.create_index([("timestamp", DESCENDING)])
    db.activity_logs.create_index([("userId", ASCENDING), ("timestamp", DESCENDING)])

    print("Indexes ensured")


def seed_admin(db) -> None:
    existing = db.users.find_one({"username": ADMIN_USERNAME})
    if existing:
        print(f"Admin already exists: {ADMIN_USERNAME}")
        return

    now = datetime.now(timezone.utc)
    db.users.insert_one(
        {
            "fullName": ADMIN_FULL_NAME,
            "username": ADMIN_USERNAME,
            "email": ADMIN_EMAIL,
            "passwordHash": bcrypt.hashpw(
                ADMIN_PASSWORD.encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8"),
            "mobile": ADMIN_MOBILE,
            "role": "admin",
            "status": True,
            "createdAt": now,
            "updatedAt": now,
        }
    )
    print(f"Admin created: {ADMIN_USERNAME}")


def ensure_storage_dirs() -> None:
    for relative in (
        "storage/clients",
        "storage/documents",
        "storage/templates",
    ):
        path = ROOT / relative
        path.mkdir(parents=True, exist_ok=True)
    print("Storage directories ensured")


def main() -> int:
    ensure_storage_dirs()

    try:
        client = _mongo_client(MONGODB_URI)
        client.admin.command("ping")
    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        print(
            "ERROR: Cannot connect to MongoDB.\n"
            f"URI: {_redacted_uri(MONGODB_URI)}\n"
            "Check Atlas Network Access (IP allowlist), DB user password,\n"
            "and that Compass uses the same cluster URI.\n"
            f"Details: {exc}",
            file=sys.stderr,
        )
        return 1

    db = client[MONGODB_DB]
    print(f"Connected -> {_redacted_uri(MONGODB_URI)} / db={MONGODB_DB}")

    ensure_collections(db)
    ensure_indexes(db)
    seed_admin(db)

    print("Done. Refresh MongoDB Compass to see the 'ndaoms' database.")
    client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
