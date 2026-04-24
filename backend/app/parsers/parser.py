"""统一解析器入口"""

from pathlib import Path
from typing import List, Optional, Tuple

from ..schemas.transaction import Transaction
from .alipay import AlipayParser, parse_alipay
from .base import read_file_with_header
from .wechat import WechatParser, parse_wechat

# 注册所有解析器
PARSERS = [AlipayParser, WechatParser]


def detect_source(file_path: Path) -> str:
    """
    检测文件来源（支付宝/微信）

    优先通过文件名检测，失败则通过内容检测
    """
    filename = file_path.name.lower()

    # 1. 通过文件名检测
    if "支付宝" in filename or "alipay" in filename:
        return "alipay"
    elif "微信" in filename or "wechat" in filename:
        return "wechat"

    # 2. 通过文件内容检测
    try:
        df = read_file_with_header(file_path)
        columns = list(df.columns)

        for parser_cls in PARSERS:
            if parser_cls.can_parse(columns):
                if parser_cls == AlipayParser:
                    return "alipay"
                elif parser_cls == WechatParser:
                    return "wechat"
    except Exception:
        pass

    # 3. 根据扩展名猜测（最后手段）
    suffix = file_path.suffix.lower()
    if suffix == ".xlsx":
        return "wechat"
    elif suffix == ".csv":
        return "alipay"

    raise ValueError(f"无法识别文件来源: {file_path.name}")


def parse_file(file_path: Path, source: Optional[str] = None) -> Tuple[List[Transaction], dict]:
    """
    解析账单文件

    Args:
        file_path: 文件路径
        source: 来源（alipay/wechat），不指定则自动检测

    Returns:
        transactions: 交易列表
        stats: 统计信息
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    if source is None:
        source = detect_source(file_path)

    if source == "alipay":
        return parse_alipay(file_path)
    elif source == "wechat":
        return parse_wechat(file_path)
    else:
        raise ValueError(f"不支持的来源: {source}")


def parse_auto(file_path: Path) -> Tuple[List[Transaction], dict, str]:
    """
    自动检测并解析文件

    Returns:
        transactions: 交易列表
        stats: 统计信息
        source: 检测到的来源
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 读取文件
    df = read_file_with_header(file_path)
    columns = list(df.columns)

    # 尝试每个解析器
    for parser_cls in PARSERS:
        if parser_cls.can_parse(columns):
            parser = parser_cls()
            transactions, stats = parser.parse(df)
            source = "alipay" if parser_cls == AlipayParser else "wechat"
            return transactions, stats, source

    raise ValueError(f"无法识别文件格式，检测到的列: {columns[:5]}...")
