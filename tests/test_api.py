from fastapi.testclient import TestClient

from app.main import app


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
