"""使用 Enum 类型替代 String

Revision ID: 005_use_enum_types
Revises: 004_add_is_admin
Create Date: 2026-04-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "005_use_enum_types"
down_revision: Union[str, None] = "004_add_is_admin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 定义 Enum 类型
source_enum = sa.Enum("alipay", "wechat", "manual", name="transaction_source")
direction_enum = sa.Enum("income", "expense", "neutral", name="transaction_direction")


def upgrade() -> None:
    # 创建 Enum 类型
    source_enum.create(op.get_bind(), checkfirst=True)
    direction_enum.create(op.get_bind(), checkfirst=True)

    # transactions 表：source 和 direction 改为 Enum
    op.execute("""
        ALTER TABLE transactions
        ALTER COLUMN source TYPE transaction_source USING source::transaction_source
    """)
    op.execute("""
        ALTER TABLE transactions
        ALTER COLUMN direction TYPE transaction_direction USING direction::transaction_direction
    """)

    # categories 表：direction 改为 Enum
    op.execute("""
        ALTER TABLE categories
        ALTER COLUMN direction TYPE transaction_direction USING direction::transaction_direction
    """)

    # upload_logs 表：source 改为 Enum
    op.execute("""
        ALTER TABLE upload_logs
        ALTER COLUMN source TYPE transaction_source USING source::transaction_source
    """)

    # parser_configs 表：source 改为 Enum
    op.execute("""
        ALTER TABLE parser_configs
        ALTER COLUMN source TYPE transaction_source USING source::transaction_source
    """)


def downgrade() -> None:
    # 改回 VARCHAR
    op.execute("ALTER TABLE transactions ALTER COLUMN source TYPE VARCHAR(20)")
    op.execute("ALTER TABLE transactions ALTER COLUMN direction TYPE VARCHAR(20)")
    op.execute("ALTER TABLE categories ALTER COLUMN direction TYPE VARCHAR(20)")
    op.execute("ALTER TABLE upload_logs ALTER COLUMN source TYPE VARCHAR(20)")
    op.execute("ALTER TABLE parser_configs ALTER COLUMN source TYPE VARCHAR(20)")

    # 删除 Enum 类型
    op.execute("DROP TYPE IF EXISTS transaction_source")
    op.execute("DROP TYPE IF EXISTS transaction_direction")
