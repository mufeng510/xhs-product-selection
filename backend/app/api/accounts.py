from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.common import dump
from app.api.deps import page_params, paginate
from app.db.session import get_db
from app.models.account import Account
from app.services.ingest import run_account_job

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


class AccountIn(BaseModel):
    source: str = "pc"
    source_user_id: str
    profile_url: str | None = None
    monitor_interval: str = "daily"
    monitor_enabled: bool = True


@router.get("")
async def list_accounts(db: AsyncSession = Depends(get_db), pages: tuple[int, int] = Depends(page_params)):
    page, size = pages
    data = await paginate(db, select(Account).order_by(Account.id.desc()), page, size)
    data["items"] = [dump(item) for item in data["items"]]
    return data


@router.post("")
async def create_account(body: AccountIn, db: AsyncSession = Depends(get_db)):
    if body.source not in {"pc", "qianfan"}:
        raise HTTPException(400, "source must be pc or qianfan")
    row = Account(**body.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return dump(row)


@router.get("/{account_id}")
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(Account, account_id)
    if not row:
        raise HTTPException(404)
    return dump(row)


@router.post("/{account_id}/run")
async def run_account(account_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(Account, account_id)
    if not row:
        raise HTTPException(404)
    await run_account_job(db, row)
    return dump(row)
