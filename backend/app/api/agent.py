from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.common import dump
from app.db.session import get_db
from app.models.account import Account
from app.models.note import Note
from app.models.product import Product

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.get("/products/trending")
async def trending(db: AsyncSession = Depends(get_db)):
    items = (await db.scalars(select(Product).order_by(Product.last_seen_at.desc()).limit(20))).all()
    return [dump(item) for item in items]


@router.get("/products/opportunities")
async def opportunities(db: AsyncSession = Depends(get_db)):
    items = (await db.scalars(select(Product).where(Product.status.in_(["NEW", "GROWING", "HOT"])).limit(20))).all()
    return [dump(item) for item in items]


@router.get("/notes/hot")
async def hot_notes(db: AsyncSession = Depends(get_db)):
    items = (await db.scalars(select(Note).where(Note.hot_score.is_not(None)).order_by(Note.hot_score.desc()).limit(20))).all()
    return [dump(item) for item in items]


@router.get("/accounts/activity")
async def account_activity(db: AsyncSession = Depends(get_db)):
    items = (await db.scalars(select(Account).order_by(Account.last_checked_at.desc().nullslast()).limit(20))).all()
    return [dump(item) for item in items]


@router.get("/dashboard/summary")
async def summary(db: AsyncSession = Depends(get_db)):
    from app.api.dashboard import dashboard

    return await dashboard(db)
