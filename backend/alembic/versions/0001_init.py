"""init schema

Revision ID: 0001_init
Revises:
Create Date: 2026-08-13
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shops",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(32), nullable=False, server_default="qianfan"),
        sa.Column("source_shop_id", sa.String(128), nullable=True),
        sa.Column("shop_name", sa.String(256), nullable=True),
        sa.Column("shop_url", sa.Text(), nullable=True),
        sa.Column("shop_type", sa.String(64), nullable=True),
        sa.Column("brand_name", sa.String(256), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_shops_source_shop_id", "shops", ["source_shop_id"])
    op.create_index("uq_shops_source_id_partial", "shops", ["source", "source_shop_id"], unique=True, postgresql_where=sa.text("source_shop_id IS NOT NULL"))

    op.create_table(
        "raw_xhs_responses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(32), server_default="xhs"),
        sa.Column("endpoint", sa.String(128), nullable=False),
        sa.Column("request_params", sa.JSON(), nullable=True),
        sa.Column("response_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_raw_endpoint", "raw_xhs_responses", ["endpoint"])
    op.create_index("ix_raw_created", "raw_xhs_responses", ["created_at"])

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(32), server_default="xhs"),
        sa.Column("source_product_id", sa.String(128), nullable=True),
        sa.Column("fingerprint", sa.String(128), nullable=True),
        sa.Column("product_name", sa.String(512), nullable=True),
        sa.Column("brand", sa.String(256), nullable=True),
        sa.Column("spec", sa.String(256), nullable=True),
        sa.Column("category_id", sa.String(128), nullable=True),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey("shops.id"), nullable=True),
        sa.Column("shop_name", sa.String(256), nullable=True),
        sa.Column("product_url", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("current_price", sa.Float(), nullable=True),
        sa.Column("current_sales", sa.Integer(), nullable=True),
        sa.Column("current_review_count", sa.Integer(), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("status", sa.String(32), server_default="NEW"),
        sa.Column("favorited", sa.Boolean(), server_default=sa.false()),
        sa.Column("tags", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_products_source_product_id", "products", ["source_product_id"])
    op.create_index("ix_products_shop_id", "products", ["shop_id"])
    op.create_index("ix_products_first_seen", "products", ["first_seen_at"])
    op.create_index("uq_products_source_id_partial", "products", ["source", "source_product_id"], unique=True, postgresql_where=sa.text("source_product_id IS NOT NULL"))
    op.create_index("uq_products_fingerprint", "products", ["fingerprint"], unique=True, postgresql_where=sa.text("fingerprint IS NOT NULL"))

    op.create_table(
        "product_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("sales", sa.Integer(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("raw_data_id", sa.Integer(), sa.ForeignKey("raw_xhs_responses.id"), nullable=True),
    )
    op.create_index("ix_psnap_product", "product_snapshots", ["product_id"])
    op.create_index("ix_psnap_captured", "product_snapshots", ["captured_at"])

    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(32), server_default="xhs"),
        sa.Column("source_note_id", sa.String(128), nullable=False),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("note_url", sa.Text(), nullable=True),
        sa.Column("author_id", sa.String(128), nullable=True),
        sa.Column("author_name", sa.String(256), nullable=True),
        sa.Column("publish_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("like_count", sa.Integer(), nullable=True),
        sa.Column("collect_count", sa.Integer(), nullable=True),
        sa.Column("comment_count", sa.Integer(), nullable=True),
        sa.Column("share_count", sa.Integer(), nullable=True),
        sa.Column("hot_score", sa.Float(), nullable=True),
        sa.Column("hot_grade", sa.String(16), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("source", "source_note_id", name="uq_notes_source_id"),
    )
    op.create_index("ix_notes_source_note_id", "notes", ["source_note_id"])
    op.create_index("ix_notes_author_id", "notes", ["author_id"])
    op.create_index("ix_notes_publish_time", "notes", ["publish_time"])

    op.create_table(
        "note_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("note_id", sa.Integer(), sa.ForeignKey("notes.id"), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("like_count", sa.Integer(), nullable=True),
        sa.Column("collect_count", sa.Integer(), nullable=True),
        sa.Column("comment_count", sa.Integer(), nullable=True),
        sa.Column("share_count", sa.Integer(), nullable=True),
        sa.Column("raw_data_id", sa.Integer(), sa.ForeignKey("raw_xhs_responses.id"), nullable=True),
    )
    op.create_index("ix_nsnap_note", "note_snapshots", ["note_id"])
    op.create_index("ix_nsnap_captured", "note_snapshots", ["captured_at"])

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(32), server_default="pc"),
        sa.Column("source_user_id", sa.String(128), nullable=False),
        sa.Column("nickname", sa.String(256), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("profile_url", sa.Text(), nullable=True),
        sa.Column("followers", sa.Integer(), nullable=True),
        sa.Column("following", sa.Integer(), nullable=True),
        sa.Column("likes_received", sa.Integer(), nullable=True),
        sa.Column("note_count", sa.Integer(), nullable=True),
        sa.Column("monitor_enabled", sa.Boolean(), server_default=sa.true()),
        sa.Column("monitor_interval", sa.String(32), server_default="daily"),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("source", "source_user_id", name="uq_accounts_source_id"),
    )
    op.create_index("ix_accounts_source_user_id", "accounts", ["source_user_id"])
    op.create_index("ix_accounts_monitor", "accounts", ["monitor_enabled"])

    op.create_table(
        "keywords",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("keyword", sa.String(256), nullable=False, unique=True),
        sa.Column("enabled", sa.Boolean(), server_default=sa.true()),
        sa.Column("fetch_count", sa.Integer(), server_default="20"),
        sa.Column("times_per_day", sa.Integer(), server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "keyword_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("keyword_id", sa.Integer(), sa.ForeignKey("keywords.id")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(32), server_default="pending"),
        sa.Column("fetched", sa.Integer(), server_default="0"),
        sa.Column("new_notes", sa.Integer(), server_default="0"),
        sa.Column("new_products", sa.Integer(), server_default="0"),
        sa.Column("failed", sa.Integer(), server_default="0"),
        sa.Column("error", sa.Text(), nullable=True),
    )
    op.create_table(
        "product_candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_note_id", sa.String(128), nullable=True),
        sa.Column("product_name", sa.String(512), nullable=True),
        sa.Column("brand", sa.String(256), nullable=True),
        sa.Column("spec", sa.String(256), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("status", sa.String(32), server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "product_matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("product_candidates.id")),
        sa.Column("target_type", sa.String(32), server_default="shop"),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey("shops.id"), nullable=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("match_score", sa.Float(), nullable=True),
        sa.Column("status", sa.String(32), server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_type", sa.String(64), nullable=False),
        sa.Column("source", sa.String(32), server_default="xhs"),
        sa.Column("status", sa.String(32), server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fetched", sa.Integer(), server_default="0"),
        sa.Column("created_count", sa.Integer(), server_default="0"),
        sa.Column("failed", sa.Integer(), server_default="0"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), server_default="pending"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    for table in [
        "notifications",
        "tasks",
        "product_matches",
        "product_candidates",
        "keyword_tasks",
        "keywords",
        "accounts",
        "note_snapshots",
        "notes",
        "product_snapshots",
        "products",
        "raw_xhs_responses",
        "shops",
    ]:
        op.drop_table(table)
