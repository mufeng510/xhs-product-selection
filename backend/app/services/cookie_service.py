"""Unified XHS cookie management.

Resolution order (first non-empty wins):
1. DB（网页「Cookie 设置」保存的值，存 app_settings 表）
2. 新环境变量 XHS_PC_COOKIE / XHS_QIANFAN_COOKIE
3. 旧环境变量 AIONE_XHS_PC_COOKIES / AIONE_XHS_QIANFAN_COOKIES / XHS_COOKIE

The effective cookie is resolved at every CLI call, so a value saved from the
web page takes effect immediately without restarting the container.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

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
    if isinstance(payload, list) and payload and isinstance(payload[0], bool):
        if not payload[0]:
            message = str(payload[1])[:200] if len(payload) > 1 and payload[1] else "接口返回失败"
            return "invalid", message
        payload = payload[2] if len(payload) >= 3 else None
    if isinstance(payload, dict):
        if payload.get("success") is False:
            return "invalid", str(payload.get("msg") or payload.get("message") or "接口返回 success=false")[:200]
        code = payload.get("code")
        if code is not None and str(code) not in ("0", "1000", "200", "success"):
            return "invalid", f"接口 code={code} {str(payload.get('msg') or '')[:150]}".strip()
        if payload.get("data") is not None:
            payload = payload["data"]
            if isinstance(payload, dict) and payload.get("success") is False:
                return "invalid", str(payload.get("msg") or "接口返回 success=false")[:200]
    return "ok", ""


async def validate(kind: str, *, run_cli: Callable[..., Any] | None = None) -> dict:
    """Probe the effective cookie with a lightweight signed request."""
    from app.adapters.xhs.cli import AioneCLI, CLIError  # 延迟导入避免与 cli.py 循环依赖

    run = run_cli or AioneCLI().run
    try:
        if kind == "pc":
            payload = await run("note", "search", {"query": "美食", "page": 1}, profile="pc")
        else:
            payload = await run("qianfan", "all-categories", {}, profile="qianfan")
        result_status, message = _interpret(payload)
    except CLIError as exc:
        result_status, message = "error", f"CLI 调用失败：{str(exc)[:200]}"
    except Exception as exc:  # noqa: BLE001
        result_status, message = "error", f"调用异常：{type(exc).__name__}: {str(exc)[:150]}"
    now = datetime.now(timezone.utc).isoformat()
    settings_store.set_json(_CHECK_KEYS[kind], {"status": result_status, "message": message, "checked_at": now})
    logger.info("cookie_check kind=%s status=%s", kind, result_status)
    return status(kind)
