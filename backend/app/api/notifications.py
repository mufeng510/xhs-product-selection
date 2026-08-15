from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.common import dump
from app.api.deps import page_params, paginate
from app.db.session import get_db
from app.models.notification import Notification
from app.notification.service import default_provider

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
async def list_notifications(db: AsyncSession = Depends(get_db), pages: tuple[int, int] = Depends(page_params)):
    page, size = pages
    data = await paginate(db, select(Notification).order_by(Notification.id.desc()), page, size)
    data["items"] = [dump(item) for item in data["items"]]
    return data


@router.post("/test")
async def test_notification():
    await default_provider().send("🔥 新爆款笔记", "测试推送")
    return {"ok": True}
