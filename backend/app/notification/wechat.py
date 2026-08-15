import logging

import httpx

from app.core.config import get_settings
from app.notification.base import NotificationProvider

logger = logging.getLogger(__name__)


class WeChatWebhookProvider(NotificationProvider):
    async def send(self, title: str, body: str) -> None:
        url = get_settings().wechat_webhook_url
        if not url:
            logger.info("wechat_webhook_skipped reason=unconfigured")
            return
        payload = {"msgtype": "text", "text": {"content": f"{title}\n{body}"}}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
