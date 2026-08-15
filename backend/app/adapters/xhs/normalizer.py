from __future__ import annotations

import logging
import re
import unicodedata
from typing import Any

logger = logging.getLogger(__name__)

QIANFAN_FIELD_MAPPING = {
    "product_id": ["product_id", "goods_id", "item_id", "sku_id", "id"],
    "product_name": ["product_name", "goods_name", "item_name", "title", "name"],
    "shop_id": ["shop_id", "seller_id", "store_id"],
    "shop_name": ["shop_name", "seller_name", "store_name"],
    "price": ["price", "sale_price", "current_price", "min_price"],
    "sales": ["sales", "sold_num", "sold_count", "sale_num"],
    "review_count": ["review_count", "comment_num", "comments", "evaluate_num"],
}

NOTE_FIELD_MAPPING = {
    "source_note_id": ["note_id", "id", "noteId"],
    "title": ["title", "display_title", "desc"],
    "content": ["desc", "content"],
    "note_url": ["note_url", "url", "link"],
    "author_id": ["user_id", "userid", "author_id", "uid"],
    "author_name": ["nickname", "nick_name", "user_name", "name"],
    "like_count": ["liked_count", "like_count", "likes"],
    "collect_count": ["collected_count", "collect_count", "collected"],
    "comment_count": ["comment_count", "comments"],
    "share_count": ["share_count", "shared_count"],
}

PROMO_WORDS = ("官方", "旗舰店", "正品", "包邮", "新品", "热销", "限时")


def first_present(data: dict[str, Any], keys: list[str], *, field: str, source: str) -> Any:
    for key in keys:
        if key in data and data[key] not in ("", [], {}):
            return data[key]
    logger.info("missing_field field=%s source=%s candidates=%s", field, source, keys)
    return None


def unwrap_cli(payload: Any) -> Any:
    if isinstance(payload, list) and payload and isinstance(payload[0], bool):
        if len(payload) >= 3:
            return payload[2]
        return None
    return payload


def as_dict_list(payload: Any) -> list[dict[str, Any]]:
    payload = unwrap_cli(payload)
    if isinstance(payload, list) and len(payload) == 2 and isinstance(payload[0], list):
        payload = payload[0]
    if isinstance(payload, dict):
        for key in ("items", "notes", "list", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [payload]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def normalize_note(raw: dict[str, Any], source: str = "xhs") -> dict[str, Any]:
    note = raw.get("note_card") if isinstance(raw.get("note_card"), dict) else raw
    user = note.get("user") if isinstance(note.get("user"), dict) else {}
    interact = note.get("interact_info") if isinstance(note.get("interact_info"), dict) else {}
    merged = {**user, **interact, **note}
    return {
        "source": source,
        "source_note_id": first_present(merged, NOTE_FIELD_MAPPING["source_note_id"], field="source_note_id", source=source),
        "title": first_present(merged, NOTE_FIELD_MAPPING["title"], field="title", source=source),
        "content": first_present(merged, NOTE_FIELD_MAPPING["content"], field="content", source=source),
        "note_url": first_present(merged, NOTE_FIELD_MAPPING["note_url"], field="note_url", source=source),
        "author_id": first_present(merged, NOTE_FIELD_MAPPING["author_id"], field="author_id", source=source),
        "author_name": first_present(merged, NOTE_FIELD_MAPPING["author_name"], field="author_name", source=source),
        "like_count": _as_int(first_present(merged, NOTE_FIELD_MAPPING["like_count"], field="like_count", source=source)),
        "collect_count": _as_int(first_present(merged, NOTE_FIELD_MAPPING["collect_count"], field="collect_count", source=source)),
        "comment_count": _as_int(first_present(merged, NOTE_FIELD_MAPPING["comment_count"], field="comment_count", source=source)),
        "share_count": _as_int(first_present(merged, NOTE_FIELD_MAPPING["share_count"], field="share_count", source=source)),
    }


def normalize_product(raw: dict[str, Any], source: str = "qianfan") -> dict[str, Any]:
    return {
        "source": source,
        "source_product_id": _as_str(first_present(raw, QIANFAN_FIELD_MAPPING["product_id"], field="product_id", source=source)),
        "product_name": first_present(raw, QIANFAN_FIELD_MAPPING["product_name"], field="product_name", source=source),
        "shop_id": _as_str(first_present(raw, QIANFAN_FIELD_MAPPING["shop_id"], field="shop_id", source=source)),
        "shop_name": first_present(raw, QIANFAN_FIELD_MAPPING["shop_name"], field="shop_name", source=source),
        "current_price": _as_float(first_present(raw, QIANFAN_FIELD_MAPPING["price"], field="price", source=source)),
        "current_sales": _as_int(first_present(raw, QIANFAN_FIELD_MAPPING["sales"], field="sales", source=source)),
        "current_review_count": _as_int(first_present(raw, QIANFAN_FIELD_MAPPING["review_count"], field="review_count", source=source)),
    }


def normalize_shop(raw: dict[str, Any], source: str = "qianfan") -> dict[str, Any]:
    return {
        "source": source,
        "source_shop_id": _as_str(first_present(raw, ["shop_id", "seller_id", "store_id", "id"], field="shop_id", source=source)),
        "shop_name": first_present(raw, ["shop_name", "seller_name", "store_name", "name"], field="shop_name", source=source),
        "shop_url": first_present(raw, ["shop_url", "url"], field="shop_url", source=source),
        "brand_name": first_present(raw, ["brand", "brand_name"], field="brand_name", source=source),
    }


def normalize_product_name(text: str | None) -> str:
    if not text:
        return ""
    value = unicodedata.normalize("NFKC", text).lower()
    value = re.sub(r"\s+", "", value)
    for word in PROMO_WORDS:
        value = value.replace(word.lower(), "")
    value = re.sub(r"[^\w\u4e00-\u9fff]", "", value)
    return value


def extract_candidates(text: str | None, source_note_id: str | None = None) -> list[dict[str, Any]]:
    if not text:
        return []
    prices = [float(item) for item in re.findall(r"(?:¥|￥)?(\d+(?:\.\d{1,2})?)", text)]
    brand = None
    for token in re.findall(r"[\u4e00-\u9fffA-Za-z]{2,12}", text):
        if token not in PROMO_WORDS:
            brand = token
            break
    name = normalize_product_name(text)[:80] or None
    return [
        {
            "source_note_id": source_note_id,
            "product_name": name,
            "brand": brand,
            "price": prices[0] if prices else None,
            "raw_text": text,
            "confidence": 40.0 if name else 10.0,
            "status": "pending",
        }
    ]


def fingerprint(brand: str | None, name: str | None, spec: str | None, shop: str | None) -> str:
    parts = [normalize_product_name(part) for part in (brand, name, spec, shop)]
    return "|".join(parts)


def _as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(str(value).replace(",", "")))
    except (TypeError, ValueError):
        return None


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", "").replace("¥", "").replace("￥", ""))
    except (TypeError, ValueError):
        return None


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
