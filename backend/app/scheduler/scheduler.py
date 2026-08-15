from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.scheduler.jobs import account_cron, keyword_cron

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(keyword_cron, "interval", hours=12, id="keyword_cron", replace_existing=True)
    scheduler.add_job(account_cron, "interval", hours=6, id="account_cron", replace_existing=True)
    scheduler.start()
