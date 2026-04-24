"""Pytest 配置"""

from pathlib import Path

import pytest


@pytest.fixture
def sample_data_dir():
    """示例数据目录"""
    return Path(__file__).parent / "data"


@pytest.fixture
def alipay_csv_content():
    """模拟支付宝 CSV 内容"""
    header_lines = "\n" * 24  # 跳过 24 行
    header = "交易时间,交易分类,交易对方,对方账号,商品说明,收/支,金额,收/付款方式,交易状态,交易订单号,商家订单号,备注"
    data = "2026-04-01 12:00:00,日用百货,测试商家,test@test.com,测试商品,支出,100.00,余额宝,交易成功,202604010001,M001,"
    return header_lines + header + "\n" + data


@pytest.fixture
def wechat_csv_content():
    """模拟微信 CSV 内容"""
    header_lines = "\n" * 17  # 跳过 17 行
    header = (
        "交易时间,交易类型,交易对方,商品,收/支,金额(元),支付方式,当前状态,交易单号,商户单号,备注"
    )
    data = (
        "2026-04-01 12:00:00,商户消费,测试商家,测试商品,支出,50.00,零钱,支付成功,WX202604010001,,"
    )
    return header_lines + header + "\n" + data
