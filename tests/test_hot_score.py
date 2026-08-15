from app.services.scoring_service import hot_score


def test_all_none():
    score, grade = hot_score(None, None, None, None, None)
    assert score is None
    assert grade is None


def test_grade_bands():
    score, grade = hot_score(100, 100, 100, 100, 100, weights={"like": 0.35, "collect": 0.3, "comment": 0.2, "engagement": 0.1, "baseline": 0.05})
    assert score == 100
    assert grade == "S"
