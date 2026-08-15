from app.adapters.xhs.normalizer import as_dict_list, normalize_shop


def test_user_by_page_shape():
    rows = as_dict_list([[{"id": "b1"}], 10])
    assert rows[0]["id"] == "b1"


def test_shop_missing_fields():
    shop = normalize_shop({"foo": 1})
    assert shop["source_shop_id"] is None
    assert shop["shop_name"] is None
