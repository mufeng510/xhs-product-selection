from __future__ import annotations

import logging
from typing import Any

from app.adapters.xhs.cli import AioneCLI, CLIError
from app.adapters.xhs.normalizer import as_dict_list, unwrap_cli
from app.adapters.xhs.redact import redact
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class XHSAdapter:
    def __init__(self, cli: AioneCLI | None = None) -> None:
        self.cli = cli or AioneCLI()
        self.settings = get_settings()

    async def search_notes(self, query: str, page: int = 1) -> list[dict[str, Any]]:
        payload = await self.cli.run("note", "search", {"query": query, "page": page}, profile="pc")
        return as_dict_list(payload)

    async def search_notes_some(self, query: str, require_num: int = 20) -> list[dict[str, Any]]:
        payload = await self.cli.run("note", "search-some", {"query": query, "require-num": require_num}, profile="pc")
        return as_dict_list(payload)

    async def get_note_info(self, url: str) -> Any:
        return unwrap_cli(await self.cli.run("note", "info", {"url": url}, profile="pc"))

    async def get_user_info(self, user_id: str) -> Any:
        return unwrap_cli(await self.cli.run("user", "info", {"user-id": user_id}, profile="pc"))

    async def get_user_notes(self, user_url: str) -> list[dict[str, Any]]:
        payload = await self.cli.run("user", "all-notes", {"user-url": user_url}, profile="pc")
        return as_dict_list(payload)

    async def get_user_comments(self, url: str) -> Any:
        return unwrap_cli(await self.cli.run("note", "all-comment", {"url": url}, profile="pc"))

    async def qianfan_categories(self) -> Any:
        return unwrap_cli(await self.cli.run("qianfan", "all-categories", {}, profile="qianfan"))

    async def qianfan_users(self, page: int = 1) -> Any:
        return await self.cli.run(
            "qianfan",
            "user-by-page",
            {"choice": "-1", "distribution-category": "unused", "page": page},
            profile="qianfan",
        )

    async def qianfan_user_detail(self, user_id: str) -> Any:
        return unwrap_cli(await self.cli.run("qianfan", "user-detail", {"user-id": user_id}, profile="qianfan"))

    async def qianfan_user_cooperation(self, user_id: str) -> Any:
        return unwrap_cli(await self.cli.run("qianfan", "user-cooperation", {"user-id": user_id}, profile="qianfan"))

    async def qianfan_user_shop(self, user_id: str) -> Any:
        if not user_id:
            raise CLIError("qianfan buyer_id required", endpoint="qianfan.user-shop")
        logger.info("qianfan_user_shop buyer_id=%s id_space=qianfan", user_id)
        return unwrap_cli(await self.cli.run("qianfan", "user-shop", {"user-id": user_id}, profile="qianfan"))

    def health(self) -> str:
        if self.cli.available() and self.cli.upstreams_present():
            return "ok"
        if self.cli.available():
            return "degraded"
        return "missing"

    @staticmethod
    def redact_payload(payload: Any) -> Any:
        return redact(payload)
