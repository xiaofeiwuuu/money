"""初始数据库表

Revision ID: 001_initial
Revises:
Create Date: 2026-04-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 用户表
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('nickname', sa.String(100), nullable=False),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # 家庭表
    op.create_table(
        'families',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('invite_code', sa.String(20), unique=True, nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_families_invite_code', 'families', ['invite_code'])

    # 家庭成员表
    op.create_table(
        'family_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('role', sa.String(20), default='member'),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_family_members_family_user', 'family_members', ['family_id', 'user_id'], unique=True)

    # 分类表
    op.create_table(
        'categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('direction', sa.String(20), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('categories.id'), nullable=True),
        sa.Column('is_system', sa.Boolean(), default=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
    )

    # 交易记录表
    op.create_table(
        'transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('source', sa.String(20), nullable=False),
        sa.Column('source_order_id', sa.String(100), nullable=False),
        sa.Column('transaction_time', sa.DateTime(), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('direction', sa.String(20), nullable=False),
        sa.Column('counterparty', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_category', sa.String(100), nullable=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('categories.id'), nullable=True),
        sa.Column('payment_method', sa.String(100), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('merchant_order_id', sa.String(100), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('is_hidden', sa.Boolean(), default=False),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_transactions_user_id', 'transactions', ['user_id'])
    op.create_index('ix_transactions_transaction_time', 'transactions', ['transaction_time'])
    op.create_index('ix_transactions_dedup', 'transactions', ['user_id', 'source', 'source_order_id'], unique=True)
    op.create_index('ix_transactions_user_time', 'transactions', ['user_id', 'transaction_time'])

    # 上传日志表
    op.create_table(
        'upload_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('source', sa.String(20), nullable=False),
        sa.Column('total_rows', sa.Integer(), default=0),
        sa.Column('success_rows', sa.Integer(), default=0),
        sa.Column('failed_rows', sa.Integer(), default=0),
        sa.Column('duplicate_rows', sa.Integer(), default=0),
        sa.Column('error_details', sa.Text(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_upload_logs_user_id', 'upload_logs', ['user_id'])


def downgrade() -> None:
    op.drop_table('upload_logs')
    op.drop_table('transactions')
    op.drop_table('categories')
    op.drop_table('family_members')
    op.drop_table('families')
    op.drop_table('users')
