from datetime import datetime, timezone

from fastapi import APIRouter

from app.adapters.xhs.adapter import XHSAdapter
from app.adapters.xhs.cli import ALLOWED, DENIED
from app.adapters.xhs.normalizer import QIANFAN_FIELD_MAPPING

router = APIRouter(prefix="/api/system", tags=["system"])

_LAST = {"ran_at": None, "fields": {}}


@router.get("/audit")
async def audit():
    adapter = XHSAdapter()
    fields = {name: False for name in QIANFAN_FIELD_MAPPING}
    _LAST["ran_at"] = datetime.now(timezone.utc).isoformat()
    _LAST["fields"] = fields
    return {
        "ran_at": _LAST["ran_at"],
        "cli": adapter.health(),
        "allowlist": [f"{r}.{a}" for r, a in sorted(ALLOWED)],
        "denylist": [f"{r}.{a}" for r, a in sorted(DENIED)],
        "product_fields": fields,
        "note": "Live field discovery requires cookies. Missing fields stay false/NULL.",
    }
