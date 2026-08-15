from app.adapters.xhs.normalizer import normalize_product


def test_missing_sales_is_none():
    data = normalize_product({"goods_id": "g1", "goods_name": "防晒"})
    assert data["source_product_id"] == "g1"
    assert data["current_sales"] is None
    assert data["current_review_count"] is None


def test_alias_sold_num():
    data = normalize_product({"goods_id": "g1", "sold_num": 12})
    assert data["current_sales"] == 12


def test_empty_not_zero():
    data = normalize_product({})
    assert data["current_sales"] is None
    assert data["current_price"] is None
