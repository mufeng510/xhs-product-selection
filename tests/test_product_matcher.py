from app.services.matcher import match_score


def test_shop_name_overlap():
    score = match_score({"product_name": "安热沙防晒", "brand": "安热沙"}, {"shop_name": "安热沙旗舰店"})
    assert score >= 50


def test_no_match_low_score():
    score = match_score({"product_name": "abc"}, {"shop_name": "xyz"})
    assert score < 50
