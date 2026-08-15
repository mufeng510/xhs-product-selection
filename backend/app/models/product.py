from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("source", "source_product_id", name="uq_products_source_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(32), default="xhs")
    source_product_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    fingerprint: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True)
    product_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(256), nullable=True)
    spec: Mapped[str | None] = mapped_column(String(256), nullable=True)
    category_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    shop_id: Mapped[int | None] = mapped_column(ForeignKey("shops.id"), nullable=True, index=True)
    shop_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    product_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_sales: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(32), default="NEW")
    favorited: Mapped[bool] = mapped_column(default=False)
    tags: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ProductSnapshot(Base):
    __tablename__ = "product_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    sales: Mapped[int | None] = mapped_column(Integer, nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_data_id: Mapped[int | None] = mapped_column(ForeignKey("raw_xhs_responses.id"), nullable=True)


class ProductCandidate(Base):
    __tablename__ = "product_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_note_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    product_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(256), nullable=True)
    spec: Mapped[str | None] = mapped_column(String(256), nullable=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProductMatch(Base):
    __tablename__ = "product_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("product_candidates.id"), index=True)
    target_type: Mapped[str] = mapped_column(String(32), default="shop")
    shop_id: Mapped[int | None] = mapped_column(ForeignKey("shops.id"), nullable=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
