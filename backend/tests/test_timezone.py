"""时区处理测试"""

from datetime import datetime, timedelta, timezone
from typing import ClassVar, List

import pytest

from app.parsers.base import BaseParser
from app.schemas.transaction import TransactionDirection, TransactionSource


class ConcreteParser(BaseParser):
    """用于测试的具体解析器"""

    IDENTIFIER_COLUMNS: ClassVar[List[str]] = ["test_col"]
    SOURCE: ClassVar[TransactionSource] = TransactionSource.ALIPAY

    def parse_direction(self, value: str) -> TransactionDirection:
        return TransactionDirection.EXPENSE


class TestParseDateTime:
    """测试日期时间解析"""

    def setup_method(self):
        self.parser = ConcreteParser()
        self.beijing_tz = timezone(timedelta(hours=8))

    def test_naive_datetime_gets_beijing_tz(self):
        """naive datetime 应该被赋予北京时区"""
        result = self.parser.parse_datetime("2026-04-01 12:00:00")

        assert result.tzinfo is not None
        assert result.tzinfo == self.beijing_tz
        assert result.hour == 12

    def test_already_aware_datetime_preserved(self):
        """已有时区的 datetime 应该保持不变"""
        utc_dt = datetime(2026, 4, 1, 4, 0, 0, tzinfo=timezone.utc)
        result = self.parser.parse_datetime(utc_dt)

        assert result.tzinfo == timezone.utc
        assert result.hour == 4  # 保持 UTC 时间

    def test_naive_datetime_object_gets_beijing_tz(self):
        """传入 naive datetime 对象也应该被赋予北京时区"""
        naive_dt = datetime(2026, 4, 1, 12, 0, 0)
        result = self.parser.parse_datetime(naive_dt)

        assert result.tzinfo == self.beijing_tz
        assert result.hour == 12

    def test_various_date_formats(self):
        """测试各种日期格式"""
        test_cases = [
            ("2026-04-01 12:00:00", 12, 0),
            ("2026/04/01 12:00:00", 12, 0),
            ("2026-04-01 12:00", 12, 0),
            ("2026/04/01 12:00", 12, 0),
            ("2026-04-01", 0, 0),
            ("2026/04/01", 0, 0),
        ]

        for date_str, expected_hour, expected_minute in test_cases:
            result = self.parser.parse_datetime(date_str)
            assert result.tzinfo == self.beijing_tz, f"Failed for {date_str}"
            assert result.hour == expected_hour, f"Failed for {date_str}"
            assert result.minute == expected_minute, f"Failed for {date_str}"

    def test_invalid_date_raises(self):
        """无效日期应该抛出异常"""
        with pytest.raises(ValueError, match="无法解析日期"):
            self.parser.parse_datetime("not-a-date")

    def test_utc_conversion_correct(self):
        """验证北京时间转 UTC 的正确性"""
        # 北京时间 2026-04-01 12:00:00 = UTC 2026-04-01 04:00:00
        result = self.parser.parse_datetime("2026-04-01 12:00:00")

        utc_result = result.astimezone(timezone.utc)
        assert utc_result.hour == 4
        assert utc_result.day == 1


class TestEnsureAware:
    """测试 _ensure_aware 函数"""

    def test_naive_becomes_aware(self):
        """naive datetime 应该被添加北京时区"""
        from app.services.transaction import _ensure_aware

        naive = datetime(2026, 4, 1, 12, 0, 0)
        result = _ensure_aware(naive)

        assert result is not None
        assert result.tzinfo is not None
        # 验证时区偏移是 +8 小时
        assert result.utcoffset() == timedelta(hours=8)

    def test_aware_unchanged(self):
        """已有时区的 datetime 应该保持不变"""
        from app.services.transaction import _ensure_aware

        utc_dt = datetime(2026, 4, 1, 4, 0, 0, tzinfo=timezone.utc)
        result = _ensure_aware(utc_dt)

        assert result.tzinfo == timezone.utc

    def test_none_returns_none(self):
        """None 应该返回 None"""
        from app.services.transaction import _ensure_aware

        assert _ensure_aware(None) is None
