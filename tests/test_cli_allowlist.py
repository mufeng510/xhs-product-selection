from app.adapters.xhs.cli import ALLOWED, DENIED


def test_choose_categories_denied():
    assert ("qianfan", "choose-categories") in DENIED
    assert ("qianfan", "choose-categories") not in ALLOWED


def test_required_commands_present():
    assert ("note", "search") in ALLOWED
    assert ("qianfan", "user-shop") in ALLOWED
