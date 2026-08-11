import socket

import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None
_ORIGINAL_GETADDRINFO = socket.getaddrinfo


def getaddrinfo_ipv4_first(
    host,
    port,
    family=0,
    type=0,
    proto=0,
    flags=0,
):
    addresses = _ORIGINAL_GETADDRINFO(host, port, family, type, proto, flags)
    ipv4_addresses = [address for address in addresses if address[0] == socket.AF_INET]
    return ipv4_addresses or addresses


def create_client(uri: str) -> AsyncIOMotorClient:
    socket.getaddrinfo = getaddrinfo_ipv4_first
    options: dict = {"serverSelectionTimeoutMS": 20_000}
    if uri.startswith("mongodb+srv://") or "tls=true" in uri.lower():
        options["tlsCAFile"] = certifi.where()
    return AsyncIOMotorClient(uri, **options)


async def connect_db() -> None:
    global client, db
    client = create_client(settings.mongodb_uri)
    db = client[settings.mongodb_db]
    await client.admin.command("ping")


async def close_db() -> None:
    global client, db
    if client is not None:
        client.close()
    client = None
    db = None


def get_db() -> AsyncIOMotorDatabase:
    if db is None:
        raise RuntimeError("Database is not connected")
    return db