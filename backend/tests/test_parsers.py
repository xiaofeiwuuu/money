"""解析器测试"""

import tempfile
from decimal import Decimal
from pathlib import Path

from app.parsers.base import detect_encoding, detect_header_row
from app.parsers.parser import detect_source, parse_file
from app.schemas.transaction import TransactionDirection, TransactionSource


class TestDetectSource:
    """测试来源检测"""

    def test_detect_alipay_by_filename(self):
        assert detect_source(Path("支付宝交易明细.csv")) == "alipay"
        assert detect_source(Path("alipay_2026.csv")) == "alipay"

    def test_detect_wechat_by_filename(self):
        assert detect_source(Path("微信支付账单.xlsx")) == "wechat"
        assert detect_source(Path("wechat_2026.xlsx")) == "wechat"

    def test_detect_by_extension(self):
        # 未知文件名时根据扩展名猜测
        assert detect_source(Path("unknown.xlsx")) == "wechat"
        assert detect_source(Path("unknown.csv")) == "alipay"


class TestAlipayParser:
    """测试支付宝解析器"""

    def test_parse_basic(self, alipay_csv_content):
        """测试基本解析"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(alipay_csv_content)
            tmp_path = Path(f.name)

        try:
            transactions, stats = parse_file(tmp_path, source="alipay")

            assert stats["total"] == 1
            assert stats["success"] == 1
            assert stats["failed"] == 0

            t = transactions[0]
            assert t.source == TransactionSource.ALIPAY
            assert t.amount == Decimal("100.00")
            assert t.direction == TransactionDirection.EXPENSE
            assert t.counterparty == "测试商家"
            assert t.source_order_id == "202604010001"
        finally:
            tmp_path.unlink()

    def test_parse_income(self):
        """测试收入解析"""
        content = "\n" * 24
        content += "交易时间,交易分类,交易对方,对方账号,商品说明,收/支,金额,收/付款方式,交易状态,交易订单号,商家订单号,备注\n"
        content += (
            "2026-04-01 12:00:00,其他,转账来源,,转账,收入,500.00,余额宝,交易成功,202604010002,,"
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = Path(f.name)

        try:
            transactions, _ = parse_file(tmp_path, source="alipay")
            assert transactions[0].direction == TransactionDirection.INCOME
            assert transactions[0].amount == Decimal("500.00")
        finally:
            tmp_path.unlink()


class TestWechatParser:
    """测试微信解析器"""

    def test_parse_basic(self, wechat_csv_content):
        """测试基本解析"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(wechat_csv_content)
            tmp_path = Path(f.name)

        try:
            transactions, stats = parse_file(tmp_path, source="wechat")

            assert stats["total"] == 1
            assert stats["success"] == 1

            t = transactions[0]
            assert t.source == TransactionSource.WECHAT
            assert t.amount == Decimal("50.00")
            assert t.direction == TransactionDirection.EXPENSE
            assert t.source_order_id == "WX202604010001"
        finally:
            tmp_path.unlink()


class TestHeaderDetection:
    """测试表头检测"""

    def test_detect_header_with_key_columns(self):
        """测试通过关键列名检测表头"""
        content = "无关内容\n无关内容\n交易时间,金额,交易对方,交易订单号\n数据行"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = Path(f.name)

        try:
            row = detect_header_row(tmp_path)
            assert row == 2  # 第 3 行（索引 2）
        finally:
            tmp_path.unlink()


class TestEncodingDetection:
    """测试编码检测"""

    def test_detect_utf8(self):
        """测试 UTF-8 编码"""
        content = "测试中文内容"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = Path(f.name)

        try:
            encoding = detect_encoding(tmp_path)
            assert encoding == "utf-8"
        finally:
            tmp_path.unlink()
