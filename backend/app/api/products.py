from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.common import dump
from app.api.deps import page_params, paginate
from app.db.session import get_db
from app.models.note import Note
from app.models.product import Product, ProductSnapshot
from app.services.scoring_service import growth

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("")
async def list_products(
    db: AsyncSession = Depends(get_db),
    pages: tuple[int, int] = Depends(page_params),
    q: str | None = None,
    status: str | None = None,
    favorited: bool | None = None,
):
    page, size = pages
    stmt = select(Product)
    if q:
        stmt = stmt.where(Product.product_name.ilike(f"%{q}%"))
    if status:
        stmt = stmt.where(Product.status == status)
    if favorited is not None:
        stmt = stmt.where(Product.favorited == favorited)
    data = await paginate(db, stmt.order_by(Product.id.desc()), page, size)
    data["items"] = [dump(item) for item in data["items"]]
    return data


@router.get("/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if not product:
        return {"detail": "not found"}
    snaps = (await db.scalars(select(ProductSnapshot).where(ProductSnapshot.product_id == product_id).order_by(ProductSnapshot.captured_at.desc()))).all()
    latest = snaps[0] if snaps else None
    prev = snaps[1] if len(snaps) > 1 else None
    payload = dump(product)
    payload["sales_growth_1d"] = growth(latest.sales if latest else None, prev.sales if prev else None)
    payload["price_change_1d"] = growth(latest.price if latest else None, prev.price if prev else None)
    payload["review_growth_1d"] = growth(latest.review_count if latest else None, prev.review_count if prev else None)
    payload["sales_growth_3d"] = None
    payload["sales_growth_7d"] = None
    payload["sales_growth_30d"] = None
    return payload


@router.get("/{product_id}/snapshots")
async def product_snapshots(product_id: int, db: AsyncSession = Depends(get_db), pages: tuple[int, int] = Depends(page_params)):
    page, size = pages
    data = await paginate(db, select(ProductSnapshot).where(ProductSnapshot.product_id == product_id).order_by(ProductSnapshot.captured_at.desc()), page, size)
    data["items"] = [dump(item) for item in data["items"]]
    return data


@router.get("/{product_id}/notes")
async def product_notes(product_id: int, db: AsyncSession = Depends(get_db), pages: tuple[int, int] = Depends(page_params)):
    page, size = pages
    data = await paginate(db, select(Note).order_by(Note.id.desc()), page, size)
    data["items"] = [dump(item) for item in data["items"]]
    return data


@router.post("/{product_id}/favorite")
async def favorite(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if not product:
        return {"detail": "not found"}
    product.favorited = True
    await db.commit()
    return dump(product)
