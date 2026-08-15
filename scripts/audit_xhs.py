#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ENDPOINTS = [
    "note.search",
    "note.info",
    "user.info",
    "user.all-notes",
    "qianfan.all-categories",
    "qianfan.user-by-page",
    "qianfan.user-detail",
    "qianfan.user-cooperation",
    "qianfan.user-shop",
]


def main() -> None:
    out = Path("/data/audit")
    if not out.exists():
        out = Path("data/audit")
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "status": "auth-missing-or-dry",
        "endpoints": {name: {"ok": False, "note": "requires cookies / aione"} for name in ENDPOINTS},
    }
    (out / "audit-summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out / "audit-summary.json")


if __name__ == "__main__":
    main()
