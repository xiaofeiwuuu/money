"""预设分类数据

Revision ID: 002_seed_categories
Revises: 001_initial
Create Date: 2026-04-24

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '002_seed_categories'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 预设分类数据
EXPENSE_CATEGORIES = [
    ("餐饮", "utensils", "#FF6B6B"),
    ("交通", "car", "#4ECDC4"),
    ("购物", "shopping-cart", "#45B7D1"),
    ("娱乐", "gamepad", "#96CEB4"),
    ("居家", "home", "#FFEAA7"),
    ("医疗", "medkit", "#DDA0DD"),
    ("教育", "book", "#98D8C8"),
    ("通讯", "phone", "#F7DC6F"),
    ("服饰", "tshirt", "#BB8FCE"),
    ("美容", "spa", "#F8B500"),
    ("社交", "users", "#85C1E9"),
    ("红包", "gift", "#E74C3C"),
    ("转账", "exchange-alt", "#9B59B6"),
    ("其他支出", "ellipsis-h", "#95A5A6"),
]

INCOME_CATEGORIES = [
    ("工资", "briefcase", "#2ECC71"),
    ("奖金", "trophy", "#F39C12"),
    ("投资", "chart-line", "#3498DB"),
    ("兼职", "laptop", "#1ABC9C"),
    ("红包收入", "gift", "#E74C3C"),
    ("退款", "undo", "#9B59B6"),
    ("报销", "file-invoice-dollar", "#16A085"),
    ("其他收入", "ellipsis-h", "#95A5A6"),
]


def upgrade() -> None:
    # 使用 bulk_insert 避免 SQL 注入风险
    categories_table = sa.table(
        "categories",
        sa.column("id", postgresql.UUID),
        sa.column("name", sa.String),
        sa.column("icon", sa.String),
        sa.column("color", sa.String),
        sa.column("direction", sa.String),
        sa.column("is_system", sa.Boolean),
    )

    # 准备数据
    rows = []
    for name, icon, color in EXPENSE_CATEGORIES:
        rows.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "icon": icon,
            "color": color,
            "direction": "expense",
            "is_system": True,
        })
    for name, icon, color in INCOME_CATEGORIES:
        rows.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "icon": icon,
            "color": color,
            "direction": "income",
            "is_system": True,
        })

    op.bulk_insert(categories_table, rows)


def downgrade() -> None:
    op.execute("DELETE FROM categories WHERE is_system = true")
