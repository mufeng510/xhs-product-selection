from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import cookie_service

router = APIRouter(prefix="/api/settings", tags=["settings"])


class CookiesIn(BaseModel):
    pc_cookie: str | None = None
    qianfan_cookie: str | None = None


@router.get("/cookies")
async def get_cookies():
    return {"cookies": cookie_service.status_all()}


@router.put("/cookies")
async def put_cookies(body: CookiesIn):
    if body.pc_cookie is None and body.qianfan_cookie is None:
        raise HTTPException(400, "pc_cookie / qianfan_cookie 至少提供一个字段；传空字符串表示清除并回退到环境变量")
    if body.pc_cookie is not None:
        cookie_service.save("pc", body.pc_cookie.strip() or None)
    if body.qianfan_cookie is not None:
        cookie_service.save("qianfan", body.qianfan_cookie.strip() or None)
    return {"cookies": cookie_service.status_all()}


@router.post("/cookies/validate")
async def validate_cookies(kind: str | None = None):
    kinds = [kind] if kind in cookie_service.KINDS else list(cookie_service.KINDS)
    results = {}
    for item in kinds:
        results[item] = await cookie_service.validate(item)
    return {"cookies": results}
