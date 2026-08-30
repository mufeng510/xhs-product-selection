import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app


@pytest.fixture()
def api_db(tmp_path, monkeypatch):
    from app.db import session as db_session
    from app.db.base import Base

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/api-test.db")

    async def _create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_create())
    monkeypatch.setattr(db_session, "engine", engine)
    monkeypatch.setattr(db_session, "SessionLocal", async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession))
    yield
    asyncio.run(engine.dispose())


def test_health_shape():
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert "status" in body
    assert "database" in body
    assert "xhs_adapter" in body


def test_audit_endpoint():
    client = TestClient(app)
    res = client.get("/api/system/audit")
    assert res.status_code == 200
    body = res.json()
    assert "product_fields" in body
    assert body["product_fields"]["sales"] is False
    assert "qianfan.choose-categories" in body["denylist"]


def test_account_crud(api_db):
    client = TestClient(app)
    created = client.post("/api/accounts", json={"source_user_id": "user-abc", "profile_url": None})
    assert created.status_code == 200
    account_id = created.json()["id"]

    listed = client.get("/api/accounts").json()
    assert listed["total"] == 1
    assert listed["items"][0]["monitor_enabled"] is True

    patched = client.patch(f"/api/accounts/{account_id}", json={"monitor_enabled": False}).json()
    assert patched["monitor_enabled"] is False

    assert client.delete(f"/api/accounts/{account_id}").json() == {"ok": True}
    assert client.get("/api/accounts").json()["total"] == 0


def test_keyword_crud(api_db):
    client = TestClient(app)
    created = client.post("/api/keywords", json={"keyword": "防晒霜", "fetch_count": 30})
    assert created.status_code == 200
    keyword_id = created.json()["id"]

    patched = client.patch(
        f"/api/keywords/{keyword_id}",
        json={"keyword": "防晒霜", "enabled": False, "fetch_count": 30, "times_per_day": 1},
    ).json()
    assert patched["enabled"] is False

    assert client.delete(f"/api/keywords/{keyword_id}").json() == {"ok": True}
