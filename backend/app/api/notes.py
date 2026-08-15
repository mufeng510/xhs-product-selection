from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.common import dump
from app.api.deps import page_params, paginate
from app.db.session import get_db
from app.models.note import Note

router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.get("")
async def list_notes(db: AsyncSession = Depends(get_db), pages: tuple[int, int] = Depends(page_params), q: str | None = None):
    page, size = pages
    stmt = select(Note)
    if q:
        stmt = stmt.where(Note.title.ilike(f"%{q}%"))
    data = await paginate(db, stmt.order_by(Note.id.desc()), page, size)
    data["items"] = [dump(item) for item in data["items"]]
    return data
