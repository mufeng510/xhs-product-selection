from __future__ import annotations

from app.adapters.xhs.normalizer import normalize_product_name


def match_score(candidate: dict, shop: dict) -> float:
    score = 0.0
    cname = normalize_product_name(candidate.get("product_name"))
    sname = normalize_product_name(shop.get("shop_name"))
    brand = normalize_product_name(candidate.get("brand"))
    if cname and sname and (cname in sname or sname in cname):
        score += 50
    if brand and sname and brand in sname:
        score += 30
    if candidate.get("price") and shop.get("shop_name"):
        score += 5
    return min(100.0, score)
