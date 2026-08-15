from app.models.account import Account


def test_account_sources():
    assert Account.__table__.c.source.default.arg == "pc"
