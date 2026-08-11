import asyncio
import socket

from httpx import ASGITransport, AsyncClient

from app.db import mongo
from app.main import app


async def get(path: str):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get(path)


def test_root_returns_api_identity() -> None:
    response = asyncio.run(get("/"))

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {"name": "NDAOMS API"},
    }


def test_health_reports_connected_database(monkeypatch) -> None:
    class FakeDatabase:
        async def command(self, name: str) -> dict:
            assert name == "ping"
            return {"ok": 1}

    monkeypatch.setattr(
        "app.modules.health.routes.get_db",
        lambda: FakeDatabase(),
    )

    response = asyncio.run(get("/api/v1/health"))

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {"status": "ok", "db": "connected"},
    }


def test_atlas_client_uses_certifi_ca_bundle(monkeypatch) -> None:
    captured: dict = {}

    def fake_client(uri: str, **kwargs):
        captured["uri"] = uri
        captured["kwargs"] = kwargs
        return object()

    monkeypatch.setattr(mongo, "AsyncIOMotorClient", fake_client)
    monkeypatch.setattr(mongo.certifi, "where", lambda: "test-ca.pem")

    result = mongo.create_client("mongodb+srv://example.mongodb.net")

    assert result is not None
    assert captured["kwargs"]["tlsCAFile"] == "test-ca.pem"
    assert captured["kwargs"]["serverSelectionTimeoutMS"] == 20_000


def test_ipv4_resolution_is_preferred_when_available(monkeypatch) -> None:
    ipv6 = (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("::1", 27017))
    ipv4 = (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 27017))
    monkeypatch.setattr(
        mongo,
        "_ORIGINAL_GETADDRINFO",
        lambda *args, **kwargs: [ipv6, ipv4],
    )

    result = mongo.getaddrinfo_ipv4_first("example.mongodb.net", 27017)

    assert result == [ipv4]
