"""Unified XHS cookie management.

Resolution order (first non-empty wins):
1. DB (web settings page, stored in app_settings table)
2. New env vars XHS_PC_COOKIE / XHS_QIANFAN_COOKIE
3. Legacy env vars AIONE_XHS_PC_COOKIES / AIONE_XHS_QIANFAN_COOKIES / XHS_COOKIE
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.services import settings_store

logger = logging.getLogger(__name__)

KINDS = ("pc", "qianfan")

_DB_KEYS = {"pc": "xhs_pc_cookie", "qianfan": "xhs_qianfan_cookie"}
_CHECK_KEYS = {"pc": "xhs_pc_cookie_check", "qianfan": "xhs_qianfan_cookie_check"}


@dataclass
class CookieInfo:
    value: str | None
    source: str  # "db" | "env" | "none"


def _env_cookie(kind: str) -> tuple[str | None, str]:
    from app.core.config import get_settings

    settings = get_settings()
    if kind == "pc":
        for name, value in (
            ("XHS_PC_COOKIE", settings.xhs_pc_cookie),
            ("AIONE_XHS_PC_COOKIES", settings.aione_xhs_pc_cookies),
            ("XHS_COOKIE", settings.xhs_cookie),
        ):
            if value:
                return value, name
        return None, ""
    for name, value in (
        ("XHS_QIANFAN_COOKIE", settings.xhs_qianfan_cookie),
        ("AIONE_XHS_QIANFAN_COOKIES", settings.aione_xhs_qianfan_cookies),
    ):
        if value:
            return value, name
    return None, ""


def resolve(kind: str) -> CookieInfo:
    db_value = settings_store.get_value(_DB_KEYS[kind])
    if db_value:
        return CookieInfo(value=db_value, source="db")
    env_value, env_name = _env_cookie(kind)
    if env_value:
        return CookieInfo(value=env_value, source=f"env:{env_name}")
    return CookieInfo(value=None, source="none")


def resolve_value(kind: str) -> str | None:
    return resolve(kind).value


def mask(cookie: str | None) -> str | None:
    if not cookie:
        return None
    if len(cookie) <= 24:
        return "已配置"
    return f"{cookie[:10]}…{cookie[-4:]}（{len(cookie)} 字符）"


def save(kind: str, value: str | None) -> dict:
    settings_store.set_value(_DB_KEYS[kind], value)
    return status(kind)


def status(kind: str) -> dict:
    info = resolve(kind)
    check = settings_store.get_json(_CHECK_KEYS[kind]) or {}
    return {
        "kind": kind,
        "configured": bool(info.value),
        "source": info.source,
        "masked": mask(info.value),
        "checked_at": check.get("checked_at"),
        "check_status": check.get("status"),
        "check_message": check.get("message"),
    }


def status_all() -> dict[str, dict]:
    return {kind: status(kind) for kind in KINDS}


def _interpret(payload: Any) -> tuple[str, str | None]:
    """Map a CLI payload to (status, message)."""
    if isinstance(payload, (list, tuple)) and payload and isinstance(payload[0], bool):
        if not payload[0]:
            message = str(payload[1])[:200] if len(payload) > 1 and payload[1] else "接口返回失败"
            return "invalid", message
        payload = payload[2] if len(payload) >= 3 else None
    if payload is None:
        return "invalid", "接口未返回数据"
    if isinstance(payload, dict):
        if payload.get("success") is False:
            return "invalid", str(payload.get("msg") or payload.get("message") or "接口返回 success=false")[:200]
        code = payload.get("code")
        if code is not None and str(code) not in ("0", "1000", "200", "success"):
            return "invalid", f"接口 code={code} {str(payload.get('msg') or '')[:150]}".strip()
        if payload.get("data") is not None:
            inner = payload["data"]
            if isinstance(inner, dict) and inner.get("success") is False:
                return "invalid", str(inner.get("msg") or "接口返回 success=false")[:200]
    if isinstance(payload, list) and len(payload) > 0:
        return "ok", ""
    return "ok", ""


async def validate(kind: str) -> dict:
    from app.adapters.xhs.adapter import XHSAdapter
    from app.adapters.xhs.cli import CLIError

    adapter = XHSAdapter()
    try:
        if kind == "pc":
            result = await adapter.search_notes("美食", page=1)
            if result:
                payload = result
            else:
                payload = None
        else:
            payload = await adapter.qianfan_categories()
        result_status, message = _interpret(payload)
    except CLIError as exc:
        result_status, message = "error", f"CLI 调用失败：{str(exc)[:200]}"
    except Exception as exc:  # noqa: BLE001
        result_status, message = "error", f"调用异常：{type(exc).__name__}: {str(exc)[:150]}"
    now = datetime.now(timezone.utc).isoformat()
    settings_store.set_json(_CHECK_KEYS[kind], {"status": result_status, "message": message, "checked_at": now})
    logger.info("cookie_check kind=%s status=%s", kind, result_status)
    return status(kind)
