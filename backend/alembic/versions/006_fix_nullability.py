"""修复 nullability 和 server_default

Revision ID: 006_fix_nullability
Revises: 005_use_enum_types
Create Date: 2026-04-24
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "006_fix_nullability"
down_revision: Union[str, None] = "005_use_enum_types"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users.is_active: 添加 NOT NULL 和 server_default
    op.execute("UPDATE users SET is_active = true WHERE is_active IS NULL")
    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text("true"),
    )

    # users.is_admin: 添加 NOT NULL 和 server_default
    op.execute("UPDATE users SET is_admin = false WHERE is_admin IS NULL")
    op.alter_column(
        "users",
        "is_admin",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text("false"),
    )

    # categories.is_system: 添加 server_default
    op.execute("UPDATE categories SET is_system = false WHERE is_system IS NULL")
    op.alter_column(
        "categories",
        "is_system",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text("false"),
    )

    # transactions.is_hidden: 添加 server_default
    op.execute("UPDATE transactions SET is_hidden = false WHERE is_hidden IS NULL")
    op.alter_column(
        "transactions",
        "is_hidden",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text("false"),
    )


def downgrade() -> None:
    # 移除 server_default（保留 nullable）
    op.alter_column("users", "is_active", server_default=None, nullable=True)
    op.alter_column("users", "is_admin", server_default=None, nullable=True)
    op.alter_column("categories", "is_system", server_default=None, nullable=True)
    op.alter_column("transactions", "is_hidden", server_default=None, nullable=True)
