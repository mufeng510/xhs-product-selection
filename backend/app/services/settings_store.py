"""Synchronous key-value store for runtime-editable settings (cookies, checks).

Uses a dedicated sync engine so it can be read from both async API handlers and
sync code paths (e.g. building CLI argv). SQLite WAL allows concurrent access.
"""

from __future__ import annotations

import json
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.engine import Engine, create_engine

from app.core.config import get_settings, sync_database_url

_ddl_ensured: set[str] = set()


@lru_cache(maxsize=4)
def _engine(url: str) -> Engine:
    return create_engine(url, pool_pre_ping=True)


def _db_url() -> str:
    return sync_database_url(get_settings().database_url)


def _connect():
    url = _db_url()
    engine = _engine(url)
    if url not in _ddl_ensured:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "CREATE TABLE IF NOT EXISTS app_settings ("
                    "key VARCHAR(128) PRIMARY KEY, "
                    "value TEXT NULL, "
                    "updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP)"
                )
            )
        _ddl_ensured.add(url)
    return engine


def get_value(key: str) -> str | None:
    with _connect().connect() as conn:
        row = conn.execute(text("SELECT value FROM app_settings WHERE key = :key"), {"key": key}).first()
    return row[0] if row else None


def set_value(key: str, value: str | None) -> None:
    with _connect().begin() as conn:
        if value is None or value == "":
            conn.execute(text("DELETE FROM app_settings WHERE key = :key"), {"key": key})
        else:
            conn.execute(
                text(
                    "INSERT INTO app_settings (key, value) VALUES (:key, :value) "
                    "ON CONFLICT (key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP"
                ),
                {"key": key, "value": value},
            )


def get_json(key: str) -> dict | None:
    raw = get_value(key)
    if not raw:
        return None
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except ValueError:
        return None


def set_json(key: str, data: dict) -> None:
    set_value(key, json.dumps(data, ensure_ascii=False))


def reset_test_state() -> None:
    """Test helper: clear the DDL guard and engine cache."""
    _ddl_ensured.clear()
    _engine.cache_clear()
