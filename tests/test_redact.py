from app.adapters.xhs.redact import redact


def test_redact_cookie_keys():
    data = redact({"cookie": "abc", "query": "防晒", "nested": {"token": "x"}})
    assert data["cookie"] == "<redacted>"
    assert data["nested"]["token"] == "<redacted>"
    assert data["query"] == "防晒"
