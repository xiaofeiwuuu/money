"""交易 API"""
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import get_current_user
from ..db.models import User, TransactionRecord
from ..services.transaction import (
    get_user_transactions,
    get_transaction_stats,
    count_user_transactions,
)

router = APIRouter()


class TransactionResponse(BaseModel):
    id: str
    source: str
    source_order_id: str
    transaction_time: datetime
    amount: str  # Decimal 字符串，避免精度丢失
    direction: str
    counterparty: str
    description: Optional[str]
    source_category: Optional[str]
    payment_method: Optional[str]
    status: str
    note: Optional[str]
    is_hidden: bool

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    items: List[TransactionResponse]
    total: int


class StatsResponse(BaseModel):
    total_income: str  # Decimal 字符串，避免精度丢失
    total_expense: str
    balance: str
    transaction_count: int


@router.get("/transactions", response_model=TransactionListResponse)
async def list_transactions(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    direction: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取交易记录列表"""
    # 并行获取数据和总数
    transactions = await get_user_transactions(
        db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        direction=direction,
        limit=limit,
        offset=offset,
    )
    total = await count_user_transactions(
        db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        direction=direction,
    )

    items = [
        TransactionResponse(
            id=str(t.id),
            source=t.source,
            source_order_id=t.source_order_id,
            transaction_time=t.transaction_time,
            amount=str(t.amount),  # Decimal -> str
            direction=t.direction,
            counterparty=t.counterparty,
            description=t.description,
            source_category=t.source_category,
            payment_method=t.payment_method,
            status=t.status,
            note=t.note,
            is_hidden=t.is_hidden,
        )
        for t in transactions
    ]

    return TransactionListResponse(items=items, total=total)


@router.get("/transactions/stats", response_model=StatsResponse)
async def get_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取统计信息"""
    stats = await get_transaction_stats(
        db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )
    return StatsResponse(**stats)


class UpdateTransactionRequest(BaseModel):
    """更新交易请求"""
    note: Optional[str] = None
    is_hidden: Optional[bool] = None


@router.patch("/transactions/{transaction_id}")
async def update_transaction(
    transaction_id: str,
    request: UpdateTransactionRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新交易记录"""
    from sqlalchemy import select
    import uuid

    try:
        tid = uuid.UUID(transaction_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的交易ID")

    result = await db.execute(
        select(TransactionRecord).where(
            TransactionRecord.id == tid,
            TransactionRecord.user_id == current_user.id,
        )
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail="交易记录不存在")

    if request.note is not None:
        transaction.note = request.note
    if request.is_hidden is not None:
        transaction.is_hidden = request.is_hidden

    await db.commit()
    return {"success": True}
