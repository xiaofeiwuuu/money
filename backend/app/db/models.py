"""SQLAlchemy 数据库模型"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
import uuid
import enum
import secrets

from sqlalchemy import (
    String, Text, Numeric, DateTime, Boolean, ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from ..core.database import Base


def utcnow():
    """获取当前 UTC 时间（带时区）"""
    return datetime.now(timezone.utc)


def generate_invite_code():
    """生成 8 位邀请码（URL 安全）"""
    return secrets.token_urlsafe(6)[:8]  # 6 bytes -> ~8 chars base64


# 枚举类型
class TransactionSourceEnum(str, enum.Enum):
    ALIPAY = "alipay"
    WECHAT = "wechat"
    MANUAL = "manual"


class TransactionDirectionEnum(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    NEUTRAL = "neutral"


# 用户模型
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    nickname: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)  # 管理员标识
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # 关系
    transactions: Mapped[List["TransactionRecord"]] = relationship(back_populates="user")
    family_memberships: Mapped[List["FamilyMember"]] = relationship(back_populates="user")
    upload_logs: Mapped[List["UploadLog"]] = relationship(back_populates="user")


# 家庭模型
class Family(Base):
    __tablename__ = "families"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    invite_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, default=generate_invite_code)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # 关系
    members: Mapped[List["FamilyMember"]] = relationship(back_populates="family")


class FamilyMember(Base):
    __tablename__ = "family_members"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    role: Mapped[str] = mapped_column(String(20), default="member")  # admin/member
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # 关系
    family: Mapped["Family"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="family_memberships")

    __table_args__ = (
        Index("ix_family_members_family_user", "family_id", "user_id", unique=True),
    )


# 分类模型
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50))
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    direction: Mapped[TransactionDirectionEnum] = mapped_column(
        SQLEnum(TransactionDirectionEnum, name="transaction_direction", create_type=False)
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)  # 系统预设分类
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # 用户自定义分类

    # 关系
    transactions: Mapped[List["TransactionRecord"]] = relationship(back_populates="category")


# 交易记录模型
class TransactionRecord(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)

    # 来源信息（用于去重）
    source: Mapped[TransactionSourceEnum] = mapped_column(
        SQLEnum(TransactionSourceEnum, name="transaction_source", create_type=False)
    )
    source_order_id: Mapped[str] = mapped_column(String(100))

    # 交易信息
    transaction_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    direction: Mapped[TransactionDirectionEnum] = mapped_column(
        SQLEnum(TransactionDirectionEnum, name="transaction_direction", create_type=False)
    )
    counterparty: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 分类
    source_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # 原始分类
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)  # 系统分类

    # 支付信息
    payment_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50))
    merchant_order_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # 扩展信息
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)  # 隐私交易
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON 数组

    # 元数据
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # 关系
    user: Mapped["User"] = relationship(back_populates="transactions")
    category: Mapped[Optional["Category"]] = relationship(back_populates="transactions")

    __table_args__ = (
        # 去重索引：同一用户 + 来源 + 订单号 唯一
        Index("ix_transactions_dedup", "user_id", "source", "source_order_id", unique=True),
        # 查询优化索引
        Index("ix_transactions_user_time", "user_id", "transaction_time"),
    )


# 解析器配置（列名映射）
class ParserConfig(Base):
    __tablename__ = "parser_configs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[TransactionSourceEnum] = mapped_column(
        SQLEnum(TransactionSourceEnum, name="transaction_source", create_type=False), index=True
    )
    field_name: Mapped[str] = mapped_column(String(50))  # transaction_time, amount, etc.
    column_aliases: Mapped[str] = mapped_column(Text)  # JSON 数组: ["交易时间", "时间"]
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    __table_args__ = (
        Index("ix_parser_config_source_field", "source", "field_name", unique=True),
    )


# 上传日志
class UploadLog(Base):
    __tablename__ = "upload_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    source: Mapped[TransactionSourceEnum] = mapped_column(
        SQLEnum(TransactionSourceEnum, name="transaction_source", create_type=False)
    )
    total_rows: Mapped[int] = mapped_column(default=0)
    success_rows: Mapped[int] = mapped_column(default=0)
    failed_rows: Mapped[int] = mapped_column(default=0)
    duplicate_rows: Mapped[int] = mapped_column(default=0)
    error_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # 关系
    user: Mapped["User"] = relationship(back_populates="upload_logs")
