from __future__ import annotations

from app.core.config import get_settings


def hot_score(
    like_velocity: float | None,
    collect_velocity: float | None,
    comment_velocity: float | None,
    engagement_rate: float | None,
    account_baseline: float | None,
    weights: dict[str, float] | None = None,
) -> tuple[float | None, str | None]:
    settings = get_settings()
    resolved = weights or {
        "like": settings.hot_like_weight,
        "collect": settings.hot_collect_weight,
        "comment": settings.hot_comment_weight,
        "engagement": settings.hot_engagement_weight,
        "baseline": settings.hot_baseline_weight,
    }
    parts = [
        like_velocity,
        collect_velocity,
        comment_velocity,
        engagement_rate,
        account_baseline,
    ]
    if all(item is None for item in parts):
        return None, None
    score = (
        (like_velocity or 0) * resolved["like"]
        + (collect_velocity or 0) * resolved["collect"]
        + (comment_velocity or 0) * resolved["comment"]
        + (engagement_rate or 0) * resolved["engagement"]
        + (account_baseline or 0) * resolved["baseline"]
    )
    normalized = max(0.0, min(100.0, score))
    if normalized >= 90:
        grade = "S"
    elif normalized >= 80:
        grade = "A"
    elif normalized >= 70:
        grade = "B"
    elif normalized >= 60:
        grade = "C"
    else:
        grade = "普通"
    return normalized, grade


def growth(current: float | int | None, previous: float | int | None) -> float | None:
    if current is None or previous is None:
        return None
    if previous == 0:
        return None
    return (float(current) - float(previous)) / float(previous)


def product_status(sales_growth_7d: float | None, note_growth: float | None) -> str:
    if sales_growth_7d is None:
        return "NEW"
    if sales_growth_7d > 1 and (note_growth or 0) > 0:
        return "HOT"
    if sales_growth_7d > 0.5:
        return "GROWING"
    if sales_growth_7d < -0.2:
        return "DECLINING"
    if sales_growth_7d > 0:
        return "POTENTIAL"
    return "MATURE"
