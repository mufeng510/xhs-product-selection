"""Direct Python API fallback for XHS when CLI fails.

The aione CLI has a bug where it tries to instantiate XHS_Apis() without
the required XHSPcAuth parameter, then falls back to calling the unbound
method without self. This module provides a direct Python API fallback.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Spider_XHS path for imports
_SPIDER_XHS_ROOT = Path("/tmp/opencode/Spider_XHS")
_ALT_SPIDER_XHS = Path("upstreams/Spider_XHS")


def _ensure_spider_xhs_on_path() -> None:
    """Add Spider_XHS to sys.path if not already present."""
    for candidate in [_SPIDER_XHS_ROOT, _ALT_SPIDER_XHS]:
        root = candidate.resolve() if candidate.exists() else candidate
        apis_dir = root / "apis"
        utils_dir = root
        for p in (str(apis_dir), str(utils_dir)):
            if p not in sys.path:
                sys.path.insert(0, p)


def _parse_cookie_to_dict(cookie_str: str) -> dict[str, str]:
    """Parse a cookie header string into a dict."""
    result: dict[str, str] = {}
    for part in cookie_str.split(";"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        key = key.strip()
        if key:
            result[key] = value.strip()
    return result


class DirectXHSApi:
    """Direct Python API wrapper that bypasses the buggy aione CLI."""

    def __init__(self) -> None:
        _ensure_spider_xhs_on_path()

    def _get_pc_auth(self, cookie: str):
        """Create XHSPcAuth from cookie string."""
        try:
            from xhs_utils.xhs_pc import XHSPcAuth
            return XHSPcAuth.from_cookie(cookie)
        except ImportError:
            logger.error("xhs_utils not available for direct API fallback")
            raise

    def _get_qianfan_api(self):
        """Create QianFanAPI instance."""
        try:
            from apis.xhs_qianfan_apis import QianFanAPI
            return QianFanAPI()
        except ImportError:
            logger.error("xhs_qianfan_apis not available for direct API fallback")
            raise

    def _parse_qianfan_cookie(self, cookie_str: str) -> dict[str, str]:
        """Parse qianfan cookie string into dict for requests."""
        return _parse_cookie_to_dict(cookie_str)

    async def search_notes(self, cookie: str, query: str, page: int = 1) -> Any:
        """Search notes using direct Python API."""
        try:
            auth = self._get_pc_auth(cookie)
            from apis.xhs_pc_apis import XHS_Apis
            apis = XHS_Apis(auth)
            # search_note is synchronous, run in executor
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: apis.search_note(query, page)
            )
            return result
        except Exception as e:
            logger.error("Direct search_notes failed: %s", e)
            raise

    async def get_note_info(self, cookie: str, url: str) -> Any:
        """Get note info using direct Python API."""
        try:
            auth = self._get_pc_auth(cookie)
            from apis.xhs_pc_apis import XHS_Apis
            apis = XHS_Apis(auth)
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: apis.get_note_info(url)
            )
            return result
        except Exception as e:
            logger.error("Direct get_note_info failed: %s", e)
            raise

    async def get_user_info(self, cookie: str, user_id: str) -> Any:
        """Get user info using direct Python API."""
        try:
            auth = self._get_pc_auth(cookie)
            from apis.xhs_pc_apis import XHS_Apis
            apis = XHS_Apis(auth)
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: apis.get_user_info(user_id)
            )
            return result
        except Exception as e:
            logger.error("Direct get_user_info failed: %s", e)
            raise

    async def get_user_notes(self, cookie: str, user_url: str) -> Any:
        """Get user notes using direct Python API."""
        try:
            auth = self._get_pc_auth(cookie)
            from apis.xhs_pc_apis import XHS_Apis
            apis = XHS_Apis(auth)
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: apis.get_user_all_notes(user_url)
            )
            return result
        except Exception as e:
            logger.error("Direct get_user_notes failed: %s", e)
            raise

    async def get_user_comments(self, cookie: str, url: str) -> Any:
        """Get user comments using direct Python API."""
        try:
            auth = self._get_pc_auth(cookie)
            from apis.xhs_pc_apis import XHS_Apis
            apis = XHS_Apis(auth)
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: apis.get_note_all_comment(url)
            )
            return result
        except Exception as e:
            logger.error("Direct get_user_comments failed: %s", e)
            raise

    async def qianfan_categories(self, cookie: str) -> Any:
        """Get qianfan categories using direct Python API."""
        try:
            api = self._get_qianfan_api()
            cookies_dict = self._parse_qianfan_cookie(cookie)
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: api.get_all_categories(cookies_dict)
            )
            return result
        except Exception as e:
            logger.error("Direct qianfan_categories failed: %s", e)
            raise

    async def qianfan_users(self, cookie: str, page: int = 1) -> Any:
        """Get qianfan users using direct Python API."""
        try:
            api = self._get_qianfan_api()
            cookies_dict = self._parse_qianfan_cookie(cookie)
            # Default: choice=-1 means all categories
            import asyncio
            loop = asyncio.get_event_loop()
            # First get categories
            categories = await loop.run_in_executor(
                None, lambda: api.get_all_categories(cookies_dict)
            )
            result = await loop.run_in_executor(
                None, lambda: api.get_user_by_page("-1", categories, page, cookies_dict)
            )
            return result
        except Exception as e:
            logger.error("Direct qianfan_users failed: %s", e)
            raise

    async def qianfan_user_detail(self, cookie: str, user_id: str) -> Any:
        """Get qianfan user detail using direct Python API."""
        try:
            api = self._get_qianfan_api()
            cookies_dict = self._parse_qianfan_cookie(cookie)
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: api.get_user_detail(user_id, cookies_dict)
            )
            return result
        except Exception as e:
            logger.error("Direct qianfan_user_detail failed: %s", e)
            raise

    async def qianfan_user_cooperation(self, cookie: str, user_id: str) -> Any:
        """Get qianfan user cooperation using direct Python API."""
        try:
            api = self._get_qianfan_api()
            cookies_dict = self._parse_qianfan_cookie(cookie)
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: api.get_user_cooperation(user_id, cookies_dict)
            )
            return result
        except Exception as e:
            logger.error("Direct qianfan_user_cooperation failed: %s", e)
            raise

    async def qianfan_user_shop(self, cookie: str, user_id: str) -> Any:
        """Get qianfan user shop using direct Python API."""
        try:
            api = self._get_qianfan_api()
            cookies_dict = self._parse_qianfan_cookie(cookie)
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: api.get_user_shop(user_id, cookies_dict)
            )
            return result
        except Exception as e:
            logger.error("Direct qianfan_user_shop failed: %s", e)
            raise
