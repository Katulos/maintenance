"""Add Refresh Tokens Table.

Revision ID: 1
Revises: 0

"""

import typing as t

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1"
down_revision: str | None = "0"
branch_labels: str | t.Sequence[str] | None = None
depends_on: str | t.Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk__refresh_tokens__user_id__users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__refresh_tokens")),
    )
    op.create_index(
        op.f("ix__refresh_tokens__expires_at"),
        "refresh_tokens",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix__refresh_tokens__token_hash"),
        "refresh_tokens",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        op.f("ix__refresh_tokens__user_id"),
        "refresh_tokens",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix__refresh_tokens__user_id"),
        table_name="refresh_tokens",
    )
    op.drop_index(
        op.f("ix__refresh_tokens__token_hash"),
        table_name="refresh_tokens",
    )
    op.drop_index(
        op.f("ix__refresh_tokens__expires_at"),
        table_name="refresh_tokens",
    )
    op.drop_table("refresh_tokens")
