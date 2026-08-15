from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Shop(Base):
    __tablename__ = "shops"
    __table_args__ = (UniqueConstraint("source", "source_shop_id", name="uq_shops_source_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(32), default="qianfan")
    source_shop_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    shop_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    shop_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    shop_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    brand_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
