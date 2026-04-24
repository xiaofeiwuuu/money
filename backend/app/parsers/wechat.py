"""微信解析器 - 支持 CSV 和 XLSX"""
from pathlib import Path
from typing import List, Tuple, Dict, Optional

from ..schemas.transaction import Transaction, TransactionDirection, TransactionSource
from .config import get_cached_aliases
from .base import BaseParser, read_file_with_header


class WechatParser(BaseParser):
    """微信账单解析器"""

    # 微信特有的列名（用于识别）
    IDENTIFIER_COLUMNS = [
        "交易单号",  # 微信使用"交易单号"
        "商户单号",
        "当前状态",
    ]

    SOURCE = TransactionSource.WECHAT

    def __init__(self, custom_aliases: Optional[Dict[str, List[str]]] = None):
        super().__init__()
        # 优先使用自定义配置，否则用缓存（内含默认回退）
        self.COLUMN_ALIASES = custom_aliases or get_cached_aliases("wechat")

    def parse_direction(self, value: str) -> TransactionDirection:
        """解析交易方向"""
        value = value.strip()
        if value == "收入":
            return TransactionDirection.INCOME
        elif value == "支出":
            return TransactionDirection.EXPENSE
        else:  # "/" 或其他表示中性交易
            return TransactionDirection.NEUTRAL


def parse_wechat(
    file_path: Path,
    custom_aliases: Optional[Dict[str, List[str]]] = None,
) -> Tuple[List[Transaction], dict]:
    """
    解析微信账单文件（支持 CSV 和 XLSX）

    自动检测表头位置和列映射
    """
    df = read_file_with_header(file_path)
    parser = WechatParser(custom_aliases=custom_aliases)

    if not parser.can_parse(list(df.columns)):
        raise ValueError("无法识别为微信账单格式，请检查文件")

    return parser.parse(df)


# 保持向后兼容
def parse_wechat_xlsx(file_path: Path) -> Tuple[List[Transaction], dict]:
    """兼容旧接口"""
    return parse_wechat(file_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        transactions, stats = parse_wechat(file_path)
        print(f"统计: {stats}")
        print(f"\n前 5 条记录:")
        for t in transactions[:5]:
            desc = t.description[:20] if t.description else ""
            print(f"  {t.transaction_time} | {t.direction.value} | {t.amount} | {t.counterparty} | {desc}")
