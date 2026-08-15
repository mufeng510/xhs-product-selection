from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RawXhsResponse(Base):
    __tablename__ = "raw_xhs_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(32), default="xhs")
    endpoint: Mapped[str] = mapped_column(String(128), index=True)
    request_params: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    response_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
