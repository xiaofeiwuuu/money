"""解析器配置表

Revision ID: 003_parser_config
Revises: 002_seed_categories
Create Date: 2026-04-24

"""

import json
import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "003_parser_config"
down_revision: Union[str, None] = "002_seed_categories"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 默认配置
ALIPAY_FIELDS = [
    ("transaction_time", ["交易时间", "交易创建时间", "创建时间", "时间"], True, "交易时间"),
    ("amount", ["金额", "金额(元)", "交易金额", "金额（元）"], True, "交易金额"),
    ("direction", ["收/支", "收/付款", "资金状态", "收支"], True, "收支方向"),
    ("counterparty", ["交易对方", "对方", "对方户名"], True, "交易对方"),
    ("description", ["商品说明", "商品名称", "商品", "备注"], False, "商品说明"),
    ("category", ["交易分类", "分类", "交易类型"], False, "交易分类"),
    ("order_id", ["交易订单号", "订单号", "交易号"], True, "订单号（用于去重）"),
    ("payment_method", ["收/付款方式", "支付方式", "付款方式"], False, "支付方式"),
    ("status", ["交易状态", "状态"], False, "交易状态"),
    ("merchant_order_id", ["商家订单号", "商户订单号"], False, "商家订单号"),
    ("note", ["备注", "说明"], False, "备注"),
]

WECHAT_FIELDS = [
    ("transaction_time", ["交易时间", "时间", "创建时间"], True, "交易时间"),
    ("amount", ["金额(元)", "金额", "金额（元）", "交易金额"], True, "交易金额"),
    ("direction", ["收/支", "收支", "资金状态"], True, "收支方向"),
    ("counterparty", ["交易对方", "对方", "对方户名"], True, "交易对方"),
    ("description", ["商品", "商品说明", "商品名称", "备注"], False, "商品说明"),
    ("category", ["交易类型", "类型", "交易分类"], False, "交易类型"),
    ("order_id", ["交易单号", "订单号", "交易号"], True, "订单号（用于去重）"),
    ("payment_method", ["支付方式", "付款方式", "收/付款方式"], False, "支付方式"),
    ("status", ["当前状态", "状态", "交易状态"], False, "交易状态"),
    ("merchant_order_id", ["商户单号", "商家订单号", "商户订单号"], False, "商户单号"),
    ("note", ["备注", "说明"], False, "备注"),
]


def upgrade() -> None:
    # 创建表
    op.create_table(
        "parser_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("field_name", sa.String(50), nullable=False),
        sa.Column("column_aliases", sa.Text(), nullable=False),
        sa.Column("is_required", sa.Boolean(), default=False),
        sa.Column("description", sa.String(200), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_parser_config_source_field", "parser_configs", ["source", "field_name"], unique=True
    )

    # 使用 bulk_insert 避免 SQL 注入风险
    from datetime import datetime

    parser_configs_table = sa.table(
        "parser_configs",
        sa.column("id", postgresql.UUID),
        sa.column("source", sa.String),
        sa.column("field_name", sa.String),
        sa.column("column_aliases", sa.Text),
        sa.column("is_required", sa.Boolean),
        sa.column("description", sa.String),
        sa.column("updated_at", sa.DateTime),
    )

    rows = []
    now = datetime.utcnow()

    for field_name, aliases, is_required, desc in ALIPAY_FIELDS:
        rows.append(
            {
                "id": str(uuid.uuid4()),
                "source": "alipay",
                "field_name": field_name,
                "column_aliases": json.dumps(aliases, ensure_ascii=False),
                "is_required": is_required,
                "description": desc,
                "updated_at": now,
            }
        )

    for field_name, aliases, is_required, desc in WECHAT_FIELDS:
        rows.append(
            {
                "id": str(uuid.uuid4()),
                "source": "wechat",
                "field_name": field_name,
                "column_aliases": json.dumps(aliases, ensure_ascii=False),
                "is_required": is_required,
                "description": desc,
                "updated_at": now,
            }
        )

    op.bulk_insert(parser_configs_table, rows)


def downgrade() -> None:
    op.drop_table("parser_configs")
