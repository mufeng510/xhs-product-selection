from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.common import dump
from app.api.deps import page_params, paginate
from app.db.session import get_db
from app.models.task import TaskRun

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("")
async def list_tasks(db: AsyncSession = Depends(get_db), pages: tuple[int, int] = Depends(page_params), status: str | None = None):
    page, size = pages
    stmt = select(TaskRun)
    if status:
        stmt = stmt.where(TaskRun.status == status)
    data = await paginate(db, stmt.order_by(TaskRun.id.desc()), page, size)
    data["items"] = [dump(item) for item in data["items"]]
    return data
