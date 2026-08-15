from app.notification.base import NotificationProvider
from app.notification.wechat import WeChatWebhookProvider


def default_provider() -> NotificationProvider:
    return WeChatWebhookProvider()
