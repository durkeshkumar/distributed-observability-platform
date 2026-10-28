
"""create workspace settings table

Revision ID: afa9efe79441
Revises: 9425adfd4122
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "afa9efe79441"
down_revision: Union[str, Sequence[str], None] = "9425adfd4122"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workspace_settings",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "workspace_name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "environment",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "timezone",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "refresh_interval",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "notification_preferences",
            sa.JSON(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("workspace_settings")
