from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:////data/app/xhs_selection.db"
    tz: str = "Asia/Shanghai"
    log_level: str = "INFO"
    xhs_profile: str = "pc"
    admin_token: str | None = None
    wechat_webhook_url: str | None = None
    aione_xhs_pc_cookies: str | None = None
    aione_xhs_qianfan_cookies: str | None = None
    xhs_cookie: str | None = None
    aione_xhs_cookies: str | None = None
    xhs_request_timeout: float = 30.0
    xhs_rate_delay: float = 1.0
    xhs_concurrency: int = 1
    hot_like_weight: float = 0.35
    hot_collect_weight: float = 0.30
    hot_comment_weight: float = 0.20
    hot_engagement_weight: float = 0.10
    hot_baseline_weight: float = 0.05
    data_dir: str = "/data/app"
    xdg_config_home: str = "/data/xhs"
    static_dir: str = "/app/static"

    def pc_cookie(self) -> str | None:
        return self.aione_xhs_pc_cookies or self.xhs_cookie or None

    def qianfan_cookie(self) -> str | None:
        return self.aione_xhs_qianfan_cookies or None


@lru_cache
def get_settings() -> Settings:
    return Settings()


def sync_database_url(url: str | None = None) -> str:
    """Convert the app DATABASE_URL to a sync SQLAlchemy URL for Alembic."""
    raw = url if url is not None else get_settings().database_url
    if "+aiosqlite" in raw:
        return raw.replace("+aiosqlite", "", 1)
    if "+asyncpg" in raw:
        return raw.replace("+asyncpg", "+psycopg2", 1)
    if raw.startswith("postgresql://"):
        return "postgresql+psycopg2://" + raw[len("postgresql://"):]
    return raw

