"""app_settings key-value store

Revision ID: 0002_app_settings
Revises: 0001_init
Create Date: 2026-08-29
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_app_settings"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(128), primary_key=True),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("app_settings")
