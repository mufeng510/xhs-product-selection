from __future__ import annotations

import asyncio
import json
import logging
import shutil
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.services import cookie_service

logger = logging.getLogger(__name__)

ALLOWED = {
    ("note", "search"),
    ("note", "search-some"),
    ("note", "info"),
    ("note", "all-comment"),
    ("user", "info"),
    ("user", "all-notes"),
    ("user", "search"),
    ("qianfan", "all-categories"),
    ("qianfan", "user-by-page"),
    ("qianfan", "user-detail"),
    ("qianfan", "user-cooperation"),
    ("qianfan", "user-shop"),
}
DENIED = {("qianfan", "choose-categories")}


class CLIError(RuntimeError):
    def __init__(self, message: str, *, endpoint: str, params: dict[str, Any] | None = None):
        super().__init__(message)
        self.endpoint = endpoint
        self.params = params or {}


class AioneCLI:
    def __init__(self) -> None:
        self.settings = get_settings()

    def available(self) -> bool:
        return shutil.which("aione") is not None

    def upstreams_present(self) -> bool:
        return Path("/app/upstreams/Spider_XHS").exists() or Path("upstreams/Spider_XHS").exists()

    async def run(self, resource: str, action: str, args: dict[str, Any] | None = None, *, profile: str = "pc") -> Any:
        if (resource, action) in DENIED:
            raise CLIError("command denylisted", endpoint=f"{resource}.{action}", params=args)
        if (resource, action) not in ALLOWED:
            raise CLIError("command not in allowlist", endpoint=f"{resource}.{action}", params=args)
        if not self.available():
            raise CLIError("aione CLI not installed", endpoint=f"{resource}.{action}", params=args)
        cmd = ["aione", "xhs", resource, action, "--output", "json"]
        for key, value in (args or {}).items():
            if value is None:
                continue
            cmd.extend([f"--{key.replace('_', '-')}", str(value)])
        cookie = cookie_service.resolve_value("pc" if profile == "pc" else "qianfan")
        if cookie:
            cmd.extend(["--cookies", cookie])
        logger.info("aione_exec endpoint=%s profile=%s", f"{resource}.{action}", profile)
        delays = [1, 3, 10]
        last_error: Exception | None = None
        for attempt, delay in enumerate([0, *delays], start=1):
            if delay:
                await asyncio.sleep(delay)
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.settings.xhs_request_timeout)
                if proc.returncode != 0:
                    raise CLIError(
                        f"aione exit={proc.returncode} stderr={stderr.decode()[:500]}",
                        endpoint=f"{resource}.{action}",
                        params=args,
                    )
                return json.loads(stdout.decode() or "null")
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning("aione_retry attempt=%s endpoint=%s error=%s", attempt, f"{resource}.{action}", exc)
        raise CLIError(str(last_error), endpoint=f"{resource}.{action}", params=args)
