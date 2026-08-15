from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.adapters.xhs.adapter import XHSAdapter
from app.api import accounts, agent, audit, dashboard, keywords, notes, notifications, products, shops, tasks
from app.core.logging import setup_logging
from app.db.session import engine
from app.scheduler.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    start_scheduler()
    yield


app = FastAPI(title="小红书选品情报系统", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(keywords.router)
app.include_router(products.router)
app.include_router(notes.router)
app.include_router(accounts.router)
app.include_router(shops.router)
app.include_router(tasks.router)
app.include_router(notifications.router)
app.include_router(dashboard.router)
app.include_router(audit.router)
app.include_router(agent.router)


@app.get("/health")
async def health():
    database = "ok"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        database = "error"
    adapter = XHSAdapter().health()
    status = "ok" if database == "ok" else "degraded"
    return {"status": status, "database": database, "xhs_adapter": adapter}
