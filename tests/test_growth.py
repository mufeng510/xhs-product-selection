from app.services.scoring_service import growth


def test_missing_history_is_none():
    assert growth(10, None) is None
    assert growth(None, 10) is None


def test_growth_value():
    assert growth(12, 10) == 0.2
