import logging

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.account import Account
from app.models.keyword import Keyword
from app.services.ingest import run_account_job, run_keyword_job

logger = logging.getLogger(__name__)


async def keyword_cron() -> None:
    async with SessionLocal() as db:
        keywords = (await db.scalars(select(Keyword).where(Keyword.enabled.is_(True)))).all()
        for keyword in keywords:
            try:
                await run_keyword_job(db, keyword)
            except Exception:
                logger.exception("keyword_cron_failed keyword_id=%s", keyword.id)


async def account_cron() -> None:
    async with SessionLocal() as db:
        accounts = (await db.scalars(select(Account).where(Account.monitor_enabled.is_(True), Account.source == "pc"))).all()
        for account in accounts:
            try:
                await run_account_job(db, account)
            except Exception:
                logger.exception("account_cron_failed account_id=%s", account.id)
