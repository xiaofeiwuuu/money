"""解析器基类和工具函数"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Tuple

import pandas as pd

from ..schemas.transaction import Transaction, TransactionDirection, TransactionSource


@dataclass
class ColumnMapping:
    """列映射配置"""

    transaction_time: str
    amount: str
    direction: str
    counterparty: str
    description: str
    category: str
    order_id: str
    payment_method: Optional[str] = None
    status: Optional[str] = None
    merchant_order_id: Optional[str] = None
    note: Optional[str] = None


class BaseParser(ABC):
    """解析器基类"""

    # 用于识别该平台的关键列名（任一匹配即可）- 子类必须 override
    IDENTIFIER_COLUMNS: ClassVar[List[str]] = []

    # 来源 - 子类必须 override
    SOURCE: ClassVar[TransactionSource] = TransactionSource.MANUAL

    def __init__(self):
        # 列名别名映射（实例变量，由子类 __init__ 填充）
        self.COLUMN_ALIASES: Dict[str, List[str]] = {}

    @classmethod
    def can_parse(cls, columns: List[str]) -> bool:
        """检查是否能解析此文件"""
        columns_lower = [c.lower().strip() for c in columns]
        return any(identifier.lower() in columns_lower for identifier in cls.IDENTIFIER_COLUMNS)

    def find_column(self, columns: List[str], aliases: List[str]) -> Optional[str]:
        """根据别名列表查找列名"""
        columns_lower = {c.lower().strip(): c for c in columns}
        for alias in aliases:
            if alias.lower() in columns_lower:
                return columns_lower[alias.lower()]
        return None

    def build_column_mapping(self, columns: List[str]) -> ColumnMapping:
        """构建列映射"""

        def get_col(key: str) -> Optional[str]:
            aliases = self.COLUMN_ALIASES.get(key, [key])
            return self.find_column(columns, aliases)

        return ColumnMapping(
            transaction_time=get_col("transaction_time") or "",
            amount=get_col("amount") or "",
            direction=get_col("direction") or "",
            counterparty=get_col("counterparty") or "",
            description=get_col("description") or "",
            category=get_col("category") or "",
            order_id=get_col("order_id") or "",
            payment_method=get_col("payment_method"),
            status=get_col("status"),
            merchant_order_id=get_col("merchant_order_id"),
            note=get_col("note"),
        )

    @abstractmethod
    def parse_direction(self, value: str) -> TransactionDirection:
        """解析交易方向"""
        pass

    def parse_amount(self, value: Any) -> Decimal:
        """解析金额"""
        if pd.isna(value):
            return Decimal("0")
        s = str(value).replace("¥", "").replace(",", "").strip()
        # 移除可能的正负号（方向由其他字段确定）
        s = s.lstrip("+-")
        try:
            return Decimal(s) if s else Decimal("0")
        except (InvalidOperation, ValueError):
            return Decimal("0")

    # 北京时区 (UTC+8)  # noqa: ERA001
    _BEIJING_TZ = timezone(timedelta(hours=8))

    def parse_datetime(self, value: Any) -> datetime:
        """解析日期时间（返回带时区的 datetime，假定账单时间为北京时间）"""
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=self._BEIJING_TZ)
            return value
        s = str(value).strip()
        # 尝试多种格式
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M",
            "%Y-%m-%d",
            "%Y/%m/%d",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(s, fmt)
                return dt.replace(tzinfo=self._BEIJING_TZ)
            except ValueError:
                continue
        raise ValueError(f"无法解析日期: {s}")

    def safe_str(self, value: Any) -> str:
        """安全转换为字符串"""
        if pd.isna(value) or value == "/" or str(value).lower() == "nan":
            return ""
        return str(value).strip()

    def parse(self, df: pd.DataFrame) -> Tuple[List[Transaction], dict]:
        """解析 DataFrame（使用 itertuples + 预计算索引提升性能）"""
        transactions = []
        stats = {"total": 0, "success": 0, "failed": 0, "errors": []}

        # 构建列映射
        mapping = self.build_column_mapping(list(df.columns))

        # 检查必需列（账单没这些列就无法解析）
        required = ["transaction_time", "amount", "order_id", "direction"]
        for field in required:
            col = getattr(mapping, field)
            if not col or col not in df.columns:
                raise ValueError(
                    f"缺少必需列: {field} (尝试匹配: {self.COLUMN_ALIASES.get(field, [field])})"
                )

        # 预计算列名到 tuple 索引的映射（+1 因为 index 在位置 0）
        col_idx = {col: i + 1 for i, col in enumerate(df.columns)}

        # 必需字段索引（上面 required 检查过，保证在 col_idx 里）
        time_idx = col_idx[mapping.transaction_time]
        amount_idx = col_idx[mapping.amount]
        direction_idx = col_idx[mapping.direction]
        order_idx = col_idx[mapping.order_id]

        # 可选字段索引（.get() 兜底，缺失时为 None，不会 KeyError）
        counterparty_idx = col_idx.get(mapping.counterparty) if mapping.counterparty else None
        desc_idx = col_idx.get(mapping.description) if mapping.description else None
        cat_idx = col_idx.get(mapping.category) if mapping.category else None
        payment_idx = col_idx.get(mapping.payment_method) if mapping.payment_method else None
        status_idx = col_idx.get(mapping.status) if mapping.status else None
        merchant_idx = col_idx.get(mapping.merchant_order_id) if mapping.merchant_order_id else None
        note_idx = col_idx.get(mapping.note) if mapping.note else None

        for row in df.itertuples(index=True, name=None):
            idx = row[0]
            stats["total"] += 1
            try:
                # 直接按索引取值，避免 dict 构造开销
                transaction = Transaction(
                    source=self.SOURCE,
                    source_order_id=self.safe_str(row[order_idx]),
                    transaction_time=self.parse_datetime(row[time_idx]),
                    amount=self.parse_amount(row[amount_idx]),
                    direction=self.parse_direction(self.safe_str(row[direction_idx])),
                    counterparty=self.safe_str(row[counterparty_idx]) if counterparty_idx else "",
                    description=self.safe_str(row[desc_idx]) if desc_idx else "",
                    source_category=self.safe_str(row[cat_idx]) if cat_idx else "",
                    payment_method=self.safe_str(row[payment_idx]) if payment_idx else "",
                    status=self.safe_str(row[status_idx]) if status_idx else "",
                    merchant_order_id=self.safe_str(row[merchant_idx]) or None
                    if merchant_idx
                    else None,
                    note=self.safe_str(row[note_idx]) or None if note_idx else None,
                )
                transactions.append(transaction)
                stats["success"] += 1
            except Exception as e:
                stats["failed"] += 1
                stats["errors"].append(f"行 {idx}: {e!s}")

        return transactions, stats


def detect_encoding(file_path: Path) -> str:
    """检测文件编码"""
    encodings = ["utf-8", "gbk", "gb2312", "gb18030", "utf-16", "latin-1"]
    for encoding in encodings:
        try:
            with file_path.open(encoding=encoding) as f:
                content = f.read(5000)
                # 检查是否有明显的中文字符
                if any("\u4e00" <= c <= "\u9fff" for c in content):
                    return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    return "utf-8"  # 默认


def detect_header_row(file_path: Path, max_rows: int = 50) -> int:
    """
    自动检测表头行号

    通过查找包含关键列名的行来确定表头位置
    """
    # 关键列名（支付宝和微信共有的）
    key_columns = ["交易时间", "金额", "交易对方", "交易单号", "交易订单号", "订单号"]

    suffix = file_path.suffix.lower()

    if suffix == ".xlsx":
        df = pd.read_excel(file_path, header=None, nrows=max_rows)
    else:
        # 检测编码
        encoding = detect_encoding(file_path)
        try:
            # 先尝试读取原始内容来检测表头
            with file_path.open(encoding=encoding) as f:
                lines = [f.readline() for _ in range(max_rows)]

            # 查找包含关键列名的行
            for row_idx, line in enumerate(lines):
                # 清理行内容
                line = line.replace("\t", "").strip()
                matches = sum(1 for key in key_columns if key in line)
                if matches >= 2:
                    return row_idx

            raise ValueError("无法检测到表头行")
        except Exception as e:
            raise ValueError(f"无法读取文件: {e}") from e

    # XLSX 文件的表头检测
    for row_idx in range(len(df)):
        row_values = [
            str(v).strip().replace("\t", "") for v in df.iloc[row_idx].values if pd.notna(v)
        ]
        matches = sum(1 for key in key_columns if any(key in v for v in row_values))
        if matches >= 2:
            return row_idx

    raise ValueError("无法检测到表头行，请确认文件格式")


def read_file_with_header(file_path: Path, header_row: Optional[int] = None) -> pd.DataFrame:
    """
    读取文件，自动检测表头

    Args:
        file_path: 文件路径
        header_row: 表头行号，None 表示自动检测
    """
    suffix = file_path.suffix.lower()

    # 自动检测表头
    if header_row is None:
        header_row = detect_header_row(file_path)

    if suffix == ".xlsx":
        df = pd.read_excel(file_path, skiprows=header_row)
    else:
        # 检测编码
        encoding = detect_encoding(file_path)
        df = pd.read_csv(file_path, skiprows=header_row, encoding=encoding)

    # 清理列名（去除制表符、空格等）
    df.columns = [str(c).strip().replace("\t", "") for c in df.columns]

    # 清理数据（去除制表符）
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(
                lambda x: str(x).strip().replace("\t", "") if pd.notna(x) else x
            )

    return df
