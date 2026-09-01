from __future__ import annotations

import logging
from typing import Any

from app.adapters.xhs.cli import AioneCLI, CLIError
from app.adapters.xhs.direct_api import DirectXHSApi
from app.adapters.xhs.normalizer import as_dict_list, unwrap_cli
from app.adapters.xhs.redact import redact
from app.core.config import get_settings
from app.services import cookie_service

logger = logging.getLogger(__name__)


def _unwrap_tuple(result: Any) -> Any:
    """Unwrap (success, msg, data) tuple from direct Python API into data."""
    if isinstance(result, (list, tuple)) and len(result) >= 3 and isinstance(result[0], bool):
        return result[2] if result[0] else None
    return result


class XHSAdapter:
    def __init__(self, cli: AioneCLI | None = None) -> None:
        self.cli = cli or AioneCLI()
        self.settings = get_settings()
        self._direct_api: DirectXHSApi | None = None

    @property
    def direct_api(self) -> DirectXHSApi:
        if self._direct_api is None:
            self._direct_api = DirectXHSApi()
        return self._direct_api

    def _should_fallback(self, exc: Exception) -> bool:
        msg = str(exc).lower()
        return (
            "missing 1 required positional argument: 'self'" in msg
            or "xhs_apis" in msg
            or "aione cli not installed" in msg
            or "upstream" in msg
            or "failed to import upstream" in msg
        )

    async def search_notes(self, query: str, page: int = 1) -> list[dict[str, Any]]:
        try:
            payload = await self.cli.run("note", "search", {"query": query, "page": page}, profile="pc")
            return as_dict_list(payload)
        except CLIError as exc:
            if self._should_fallback(exc):
                logger.warning("CLI fallback for search_notes: %s", exc)
                cookie = cookie_service.resolve_value("pc")
                if cookie:
                    result = await self.direct_api.search_notes(cookie, query, page)
                    return as_dict_list(_unwrap_tuple(result))
            raise

    async def search_notes_some(self, query: str, require_num: int = 20) -> list[dict[str, Any]]:
        try:
            payload = await self.cli.run("note", "search-some", {"query": query, "require-num": require_num}, profile="pc")
            return as_dict_list(payload)
        except CLIError as exc:
            if self._should_fallback(exc):
                logger.warning("CLI fallback for search_notes_some: %s", exc)
                cookie = cookie_service.resolve_value("pc")
                if cookie:
                    result = await self.direct_api.search_notes(cookie, query, page=1)
                    return as_dict_list(_unwrap_tuple(result))
            raise

    async def get_note_info(self, url: str) -> Any:
        try:
            return unwrap_cli(await self.cli.run("note", "info", {"url": url}, profile="pc"))
        except CLIError as exc:
            if self._should_fallback(exc):
                logger.warning("CLI fallback for get_note_info: %s", exc)
                cookie = cookie_service.resolve_value("pc")
                if cookie:
                    result = await self.direct_api.get_note_info(cookie, url)
                    return unwrap_cli(_unwrap_tuple(result))
            raise

    async def get_user_info(self, user_id: str) -> Any:
        try:
            return unwrap_cli(await self.cli.run("user", "info", {"user-id": user_id}, profile="pc"))
        except CLIError as exc:
            if self._should_fallback(exc):
                logger.warning("CLI fallback for get_user_info: %s", exc)
                cookie = cookie_service.resolve_value("pc")
                if cookie:
                    result = await self.direct_api.get_user_info(cookie, user_id)
                    return unwrap_cli(_unwrap_tuple(result))
            raise

    async def get_user_notes(self, user_url: str) -> list[dict[str, Any]]:
        try:
            payload = await self.cli.run("user", "all-notes", {"user-url": user_url}, profile="pc")
            return as_dict_list(payload)
        except CLIError as exc:
            if self._should_fallback(exc):
                logger.warning("CLI fallback for get_user_notes: %s", exc)
                cookie = cookie_service.resolve_value("pc")
                if cookie:
                    result = await self.direct_api.get_user_notes(cookie, user_url)
                    return as_dict_list(_unwrap_tuple(result))
            raise

    async def get_user_comments(self, url: str) -> Any:
        try:
            return unwrap_cli(await self.cli.run("note", "all-comment", {"url": url}, profile="pc"))
        except CLIError as exc:
            if self._should_fallback(exc):
                logger.warning("CLI fallback for get_user_comments: %s", exc)
                cookie = cookie_service.resolve_value("pc")
                if cookie:
                    result = await self.direct_api.get_user_comments(cookie, url)
                    return unwrap_cli(_unwrap_tuple(result))
            raise

    async def qianfan_categories(self) -> Any:
        try:
            return unwrap_cli(await self.cli.run("qianfan", "all-categories", {}, profile="qianfan"))
        except CLIError as exc:
            if self._should_fallback(exc):
                logger.warning("CLI fallback for qianfan_categories: %s", exc)
                cookie = cookie_service.resolve_value("qianfan")
                if cookie:
                    result = await self.direct_api.qianfan_categories(cookie)
                    return unwrap_cli(result)
            raise

    async def qianfan_users(self, page: int = 1) -> Any:
        try:
            return await self.cli.run(
                "qianfan",
                "user-by-page",
                {"choice": "-1", "distribution-category": "unused", "page": page},
                profile="qianfan",
            )
        except CLIError as exc:
            if self._should_fallback(exc):
                logger.warning("CLI fallback for qianfan_users: %s", exc)
                cookie = cookie_service.resolve_value("qianfan")
                if cookie:
                    return await self.direct_api.qianfan_users(cookie, page)
            raise

    async def qianfan_user_detail(self, user_id: str) -> Any:
        try:
            return unwrap_cli(await self.cli.run("qianfan", "user-detail", {"user-id": user_id}, profile="qianfan"))
        except CLIError as exc:
            if self._should_fallback(exc):
                logger.warning("CLI fallback for qianfan_user_detail: %s", exc)
                cookie = cookie_service.resolve_value("qianfan")
                if cookie:
                    result = await self.direct_api.qianfan_user_detail(cookie, user_id)
                    return unwrap_cli(result)
            raise

    async def qianfan_user_cooperation(self, user_id: str) -> Any:
        try:
            return unwrap_cli(await self.cli.run("qianfan", "user-cooperation", {"user-id": user_id}, profile="qianfan"))
        except CLIError as exc:
            if self._should_fallback(exc):
                logger.warning("CLI fallback for qianfan_user_cooperation: %s", exc)
                cookie = cookie_service.resolve_value("qianfan")
                if cookie:
                    result = await self.direct_api.qianfan_user_cooperation(cookie, user_id)
                    return unwrap_cli(result)
            raise

    async def qianfan_user_shop(self, user_id: str) -> Any:
        if not user_id:
            raise CLIError("qianfan buyer_id required", endpoint="qianfan.user-shop")
        logger.info("qianfan_user_shop buyer_id=%s id_space=qianfan", user_id)
        try:
            return unwrap_cli(await self.cli.run("qianfan", "user-shop", {"user-id": user_id}, profile="qianfan"))
        except CLIError as exc:
            if self._should_fallback(exc):
                logger.warning("CLI fallback for qianfan_user_shop: %s", exc)
                cookie = cookie_service.resolve_value("qianfan")
                if cookie:
                    result = await self.direct_api.qianfan_user_shop(cookie, user_id)
                    return unwrap_cli(result)
            raise

    def health(self) -> str:
        if self.cli.available() and self.cli.upstreams_present():
            return "ok"
        if self.cli.available():
            return "degraded"
        return "missing"

    @staticmethod
    def redact_payload(payload: Any) -> Any:
        return redact(payload)
