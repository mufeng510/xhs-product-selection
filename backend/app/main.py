from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import text

from app.adapters.xhs.adapter import XHSAdapter
from app.api import accounts, agent, audit, dashboard, keywords, notes, notifications, products, shops, tasks
from app.core.config import get_settings
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


static_root = Path(get_settings().static_dir).resolve()
if static_root.is_dir():

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        candidate = (static_root / full_path).resolve()
        if full_path and candidate.is_file() and candidate.is_relative_to(static_root):
            return FileResponse(candidate)
        html = candidate.with_suffix(".html") if full_path else static_root / "index.html"
        if html.is_file() and html.is_relative_to(static_root):
            return FileResponse(html)
        index = candidate / "index.html" if candidate.is_dir() else None
        if index and index.is_file() and index.is_relative_to(static_root):
            return FileResponse(index)
        if full_path.startswith(("api/", "health")):
            raise HTTPException(status_code=404)
        not_found = static_root / "404.html"
        if not_found.is_file():
            return FileResponse(not_found, status_code=404)
        return FileResponse(static_root / "index.html")
