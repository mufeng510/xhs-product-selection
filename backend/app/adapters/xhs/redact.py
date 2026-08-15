from __future__ import annotations

import copy
from typing import Any

SENSITIVE_KEYS = {
    "cookie",
    "cookies",
    "cookies_str",
    "token",
    "xsec_token",
    "authorization",
    "sid",
    "sessionid",
    "passport_csrf_token",
}


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if str(key).lower() in SENSITIVE_KEYS:
                out[key] = "<redacted>"
            else:
                out[key] = redact(item)
        return out
    if isinstance(value, list):
        return [redact(item) for item in value]
    return copy.deepcopy(value)
