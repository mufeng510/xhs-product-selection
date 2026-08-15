from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.common import dump
from app.api.deps import page_params, paginate
from app.db.session import get_db
from app.models.shop import Shop

router = APIRouter(prefix="/api/shops", tags=["shops"])


@router.get("")
async def list_shops(db: AsyncSession = Depends(get_db), pages: tuple[int, int] = Depends(page_params)):
    page, size = pages
    data = await paginate(db, select(Shop).order_by(Shop.id.desc()), page, size)
    data["items"] = [dump(item) for item in data["items"]]
    return data
