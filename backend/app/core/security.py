from fastapi import Header, HTTPException

from app.core.config import get_settings


async def optional_admin(x_admin_token: str | None = Header(default=None)) -> None:
    token = get_settings().admin_token
    if not token:
        return
    if x_admin_token != token:
        raise HTTPException(status_code=401, detail="invalid admin token")
