from typing import Any

from fastapi import Query
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def paginate(db: AsyncSession, stmt: Select, page: int, page_size: int) -> dict[str, Any]:
    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = (await db.scalars(stmt.offset((page - 1) * page_size).limit(page_size))).all()
    return {"page": page, "page_size": page_size, "total": int(total or 0), "items": items}


def page_params(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)) -> tuple[int, int]:
    return page, page_size
