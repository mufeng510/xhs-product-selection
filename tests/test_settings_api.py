import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import cookie_service, settings_store


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "settings-api-test.db"
    settings_store.reset_test_state()
    monkeypatch.setattr(settings_store, "_db_url", lambda: f"sqlite:///{db_path}")
    yield TestClient(app)
    settings_store.reset_test_state()


def test_cookie_settings_flow(client):
    data = client.get("/api/settings/cookies").json()["cookies"]
    assert data["pc"]["configured"] is False
    assert data["pc"]["source"] == "none"

    cookie = "webclid=" + "c" * 120 + "; web_session=secret1234567890abcd"
    data = client.put("/api/settings/cookies", json={"pc_cookie": cookie}).json()["cookies"]
    assert data["pc"]["configured"] is True
    assert data["pc"]["source"] == "db"
    assert "secret1234567890abcd" not in data["pc"]["masked"]
    assert data["pc"]["masked"] == cookie_service.mask(cookie)

    cleared = client.put("/api/settings/cookies", json={"pc_cookie": ""}).json()["cookies"]
    assert cleared["pc"]["configured"] is False


def test_put_requires_at_least_one_field(client):
    response = client.put("/api/settings/cookies", json={})
    assert response.status_code == 400


def test_validate_endpoint_runs_probe(client, monkeypatch):
    async def fake_validate(kind, *, run_cli=None):
        cookie_service.save(kind, "z" * 50)
        return {
            "kind": kind,
            "configured": True,
            "source": "db",
            "masked": cookie_service.mask("z" * 50),
            "checked_at": "2026-08-29T00:00:00+00:00",
            "check_status": "ok",
            "check_message": "",
        }

    monkeypatch.setattr(cookie_service, "validate", fake_validate)
    data = client.post("/api/settings/cookies/validate").json()["cookies"]
    assert set(data) == {"pc", "qianfan"}
    assert data["pc"]["check_status"] == "ok"
