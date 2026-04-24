"""统一交易数据模型（解析后、入库前）"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

# 从 db.models 导入 Enum，保持单一定义
from ..db.models import TransactionDirectionEnum as TransactionDirection
from ..db.models import TransactionSourceEnum as TransactionSource


@dataclass
class Transaction:
    """统一交易记录"""

    source: TransactionSource
    source_order_id: str  # 原始订单号，用于去重
    transaction_time: datetime
    amount: Decimal
    direction: TransactionDirection
    counterparty: str  # 交易对方
    description: str  # 商品说明
    source_category: str  # 原始分类
    payment_method: str  # 支付方式
    status: str  # 交易状态
    merchant_order_id: Optional[str] = None  # 商家订单号
    note: Optional[str] = None  # 备注

    def to_dict(self) -> dict:
        return {
            "source": self.source.value,
            "source_order_id": self.source_order_id,
            "transaction_time": self.transaction_time.isoformat(),
            "amount": str(self.amount),
            "direction": self.direction.value,
            "counterparty": self.counterparty,
            "description": self.description,
            "source_category": self.source_category,
            "payment_method": self.payment_method,
            "status": self.status,
            "merchant_order_id": self.merchant_order_id,
            "note": self.note,
        }
