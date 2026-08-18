import inspect

import psycopg2

from app.core.config import sync_database_url


def test_psycopg2_is_importable():
    assert psycopg2.__name__ == "psycopg2"


def test_asyncpg_url_becomes_psycopg2():
    url = "postgresql+asyncpg://xhs:change_me@postgres:5432/xhs_selection"
    assert sync_database_url(url) == "postgresql+psycopg2://xhs:change_me@postgres:5432/xhs_selection"


def test_bare_postgres_url_becomes_psycopg2():
    url = "postgresql://xhs:change_me@postgres:5432/xhs_selection"
    assert sync_database_url(url) == "postgresql+psycopg2://xhs:change_me@postgres:5432/xhs_selection"


def test_alembic_env_calls_sync_database_url():
    from pathlib import Path

    source = (Path(__file__).resolve().parents[1] / "backend" / "alembic" / "env.py").read_text()
    assert "sync_database_url" in source
    assert "psycopg2" in inspect.getsource(sync_database_url)
