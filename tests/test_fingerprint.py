from app.adapters.xhs.normalizer import fingerprint, normalize_product_name


def test_normalize_strips_promo():
    assert "旗舰店" not in normalize_product_name("XX防晒霜官方旗舰店正品50ml")


def test_fingerprint_stable():
    assert fingerprint("A", "防晒", "50ml", "shop") == fingerprint("a", "防晒", "50ml", "shop")
