from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.common import dump
from app.db.session import get_db
from app.models.account import Account
from app.models.note import Note
from app.models.product import Product

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
async def dashboard(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    day = now - timedelta(days=1)
    week = now - timedelta(days=7)
    new_products_24h = await db.scalar(select(func.count()).select_from(Product).where(Product.first_seen_at >= day))
    new_products_7d = await db.scalar(select(func.count()).select_from(Product).where(Product.first_seen_at >= week))
    new_notes = await db.scalar(select(func.count()).select_from(Note).where(Note.created_at >= day))
    hot = (await db.scalars(select(Note).where(Note.hot_score.is_not(None)).order_by(Note.hot_score.desc()).limit(10))).all()
    newest = (await db.scalars(select(Product).order_by(Product.first_seen_at.desc()).limit(10))).all()
    accounts = await db.scalar(select(func.count()).select_from(Account).where(Account.monitor_enabled.is_(True)))
    return {
        "today_new_products": int(new_products_24h or 0),
        "week_new_products": int(new_products_7d or 0),
        "today_new_notes": int(new_notes or 0),
        "hot_notes": [dump(item) for item in hot],
        "new_products": [dump(item) for item in newest],
        "monitored_accounts": int(accounts or 0),
    }
