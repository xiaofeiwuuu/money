"""交易服务"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import case, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import TransactionRecord, UploadLog
from ..schemas.transaction import Transaction


async def save_transactions(
    db: AsyncSession,
    user_id: uuid.UUID,
    transactions: List[Transaction],
    filename: str,
) -> Tuple[int, int, int]:
    """
    批量保存交易记录（带去重）

    使用批量插入优化性能，一次请求完成所有插入。
    返回: (成功数, 重复数, 失败数)
    """
    if not transactions:
        return 0, 0, 0

    errors = []

    # 准备批量数据
    values = []
    for t in transactions:
        # manual 来源自动生成订单号（避免空订单号冲突）
        source_order_id = t.source_order_id
        if t.source.value == "manual" and not source_order_id:
            source_order_id = str(uuid.uuid4())

        values.append(
            {
                "user_id": user_id,
                "source": t.source.value,
                "source_order_id": source_order_id,
                "transaction_time": t.transaction_time,
                "amount": t.amount,
                "direction": t.direction.value,
                "counterparty": t.counterparty,
                "description": t.description,
                "source_category": t.source_category,
                "payment_method": t.payment_method,
                "status": t.status,
                "merchant_order_id": t.merchant_order_id,
                "note": t.note,
            }
        )

    try:
        # 批量插入，冲突时跳过
        stmt = insert(TransactionRecord).values(values)
        stmt = stmt.on_conflict_do_nothing(index_elements=["user_id", "source", "source_order_id"])
        # 返回插入的行数
        stmt = stmt.returning(TransactionRecord.id)

        result = await db.execute(stmt)
        inserted_ids = result.fetchall()
        success_count = len(inserted_ids)
        duplicate_count = len(values) - success_count
        failed_count = 0

    except Exception as e:
        # 批量插入失败，必须先 rollback 再重试
        await db.rollback()
        errors.append(f"批量插入失败: {e!s}")
        success_count = 0
        duplicate_count = 0
        failed_count = 0

        for i, val in enumerate(values):
            try:
                # 使用 savepoint 保护每条插入，失败时只回滚当前行
                async with db.begin_nested():
                    stmt = insert(TransactionRecord).values(**val)
                    stmt = stmt.on_conflict_do_nothing(
                        index_elements=["user_id", "source", "source_order_id"]
                    )
                    result = await db.execute(stmt)
                    if result.rowcount > 0:
                        success_count += 1
                    else:
                        duplicate_count += 1
            except Exception as row_e:
                # savepoint 已自动回滚，无需手动 rollback
                failed_count += 1
                errors.append(f"行 {i}: {row_e!s}")

    # 记录上传日志（在同一事务中提交，保证原子性）
    # transactions 非空已在函数开头检查
    log = UploadLog(
        user_id=user_id,
        filename=filename,
        source=transactions[0].source.value,
        total_rows=len(transactions),
        success_rows=success_count,
        failed_rows=failed_count,
        duplicate_rows=duplicate_count,
        error_details=json.dumps(errors, ensure_ascii=False) if errors else None,
    )
    db.add(log)

    # 单次提交：交易记录 + 上传日志
    await db.commit()

    return success_count, duplicate_count, failed_count


def _apply_transaction_filters(query, user_id, start_date, end_date, direction):
    """应用交易过滤条件"""
    query = query.where(TransactionRecord.user_id == user_id)
    if start_date:
        query = query.where(TransactionRecord.transaction_time >= start_date)
    if end_date:
        # end_date + 1 天，确保包含当天
        query = query.where(TransactionRecord.transaction_time < end_date + timedelta(days=1))
    if direction:
        query = query.where(TransactionRecord.direction == direction)
    return query


async def count_user_transactions(
    db: AsyncSession,
    user_id: uuid.UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    direction: Optional[str] = None,
) -> int:
    """获取用户交易记录总数"""
    query = select(func.count(TransactionRecord.id))
    query = _apply_transaction_filters(query, user_id, start_date, end_date, direction)
    result = await db.execute(query)
    return result.scalar() or 0


async def get_user_transactions(
    db: AsyncSession,
    user_id: uuid.UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    direction: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[TransactionRecord]:
    """获取用户交易记录"""
    query = select(TransactionRecord)
    query = _apply_transaction_filters(query, user_id, start_date, end_date, direction)
    query = query.order_by(TransactionRecord.transaction_time.desc())
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def get_transaction_stats(
    db: AsyncSession,
    user_id: uuid.UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict:
    """获取统计信息（单次查询，使用 FILTER 优化）"""
    # 构建基础查询
    query = select(
        func.sum(
            case((TransactionRecord.direction == "income", TransactionRecord.amount), else_=0)
        ).label("income"),
        func.sum(
            case((TransactionRecord.direction == "expense", TransactionRecord.amount), else_=0)
        ).label("expense"),
        func.count(TransactionRecord.id).label("count"),
    ).where(TransactionRecord.user_id == user_id)

    # 日期过滤（与 list 保持一致）
    if start_date:
        query = query.where(TransactionRecord.transaction_time >= start_date)
    if end_date:
        query = query.where(TransactionRecord.transaction_time < end_date + timedelta(days=1))

    result = await db.execute(query)
    row = result.one()

    income = row.income or 0
    expense = row.expense or 0

    return {
        "total_income": str(income),  # 统一用字符串，避免精度丢失
        "total_expense": str(expense),
        "balance": str(income - expense),
        "transaction_count": row.count or 0,
    }
