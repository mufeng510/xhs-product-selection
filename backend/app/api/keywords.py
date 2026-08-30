from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.common import dump
from app.api.deps import page_params, paginate
from app.db.session import get_db
from app.models.keyword import Keyword, KeywordTask
from app.services.ingest import run_keyword_job

router = APIRouter(prefix="/api/keywords", tags=["keywords"])


class KeywordIn(BaseModel):
    keyword: str
    enabled: bool = True
    fetch_count: int = 20
    times_per_day: int = 1


@router.get("")
async def list_keywords(db: AsyncSession = Depends(get_db), pages: tuple[int, int] = Depends(page_params)):
    page, size = pages
    data = await paginate(db, select(Keyword).order_by(Keyword.id.desc()), page, size)
    data["items"] = [dump(item) for item in data["items"]]
    return data


@router.post("")
async def create_keyword(body: KeywordIn, db: AsyncSession = Depends(get_db)):
    row = Keyword(**body.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return dump(row)


@router.patch("/{keyword_id}")
async def update_keyword(keyword_id: int, body: KeywordIn, db: AsyncSession = Depends(get_db)):
    row = await db.get(Keyword, keyword_id)
    if not row:
        raise HTTPException(404)
    for key, value in body.model_dump().items():
        setattr(row, key, value)
    await db.commit()
    return dump(row)


@router.delete("/{keyword_id}")
async def delete_keyword(keyword_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(Keyword, keyword_id)
    if not row:
        raise HTTPException(404)
    await db.delete(row)
    await db.commit()
    return {"ok": True}


@router.post("/{keyword_id}/run")
async def run_keyword(keyword_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(Keyword, keyword_id)
    if not row:
        raise HTTPException(404)
    try:
        task = await run_keyword_job(db, row)
    except Exception:
        # run_keyword_job 已把失败写入 keyword_tasks；返回失败任务让前端能看到具体原因
        task = (await db.scalars(select(KeywordTask).where(KeywordTask.keyword_id == row.id).order_by(KeywordTask.id.desc()))).first()
        if task is None:
            raise HTTPException(500, "任务执行失败且未留下记录")
    return dump(task)


@router.get("/{keyword_id}/tasks")
async def keyword_tasks(keyword_id: int, db: AsyncSession = Depends(get_db), pages: tuple[int, int] = Depends(page_params)):
    page, size = pages
    data = await paginate(db, select(KeywordTask).where(KeywordTask.keyword_id == keyword_id).order_by(KeywordTask.id.desc()), page, size)
    data["items"] = [dump(item) for item in data["items"]]
    return data
