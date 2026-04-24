"""支付宝解析器 - 支持 CSV 和 XLSX"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..schemas.transaction import Transaction, TransactionDirection, TransactionSource
from .base import BaseParser, read_file_with_header
from .config import get_cached_aliases


class AlipayParser(BaseParser):
    """支付宝账单解析器"""

    # 支付宝特有的列名（用于识别）
    IDENTIFIER_COLUMNS = [
        "交易订单号",  # 支付宝使用"交易订单号"
        "商家订单号",
        "对方账号",
    ]

    SOURCE = TransactionSource.ALIPAY

    def __init__(self, custom_aliases: Optional[Dict[str, List[str]]] = None):
        super().__init__()
        # 优先使用自定义配置，否则用缓存（内含默认回退）
        self.COLUMN_ALIASES = custom_aliases or get_cached_aliases("alipay")

    def parse_direction(self, value: str) -> TransactionDirection:
        """解析交易方向"""
        value = value.strip()
        if value == "收入":
            return TransactionDirection.INCOME
        elif value == "支出":
            return TransactionDirection.EXPENSE
        else:
            return TransactionDirection.NEUTRAL


def parse_alipay(
    file_path: Path,
    custom_aliases: Optional[Dict[str, List[str]]] = None,
) -> Tuple[List[Transaction], dict]:
    """
    解析支付宝账单文件（支持 CSV 和 XLSX）

    自动检测表头位置和列映射
    """
    df = read_file_with_header(file_path)
    parser = AlipayParser(custom_aliases=custom_aliases)

    if not parser.can_parse(list(df.columns)):
        raise ValueError("无法识别为支付宝账单格式，请检查文件")

    return parser.parse(df)


# 保持向后兼容
def parse_alipay_csv(file_path: Path) -> Tuple[List[Transaction], dict]:
    """兼容旧接口"""
    return parse_alipay(file_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        transactions, stats = parse_alipay(file_path)
        print(f"统计: {stats}")
        print("\n前 5 条记录:")
        for t in transactions[:5]:
            print(f"  {t.transaction_time} | {t.direction.value} | {t.amount} | {t.counterparty}")
