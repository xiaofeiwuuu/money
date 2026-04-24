#!/usr/bin/env python3
"""测试解析器"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.parsers.parser import parse_file
from app.schemas.transaction import TransactionDirection


def test_alipay():
    """测试支付宝解析"""
    file_path = Path(__file__).parent.parent / "支付宝交易明细(20260101-20260408)_utf8.csv"
    if not file_path.exists():
        print(f"❌ 支付宝文件不存在: {file_path}")
        return

    print("=" * 60)
    print("支付宝账单解析测试")
    print("=" * 60)

    transactions, stats = parse_file(file_path)

    print("\n📊 统计:")
    print(f"   总行数: {stats['total']}")
    print(f"   成功: {stats['success']}")
    print(f"   失败: {stats['failed']}")

    if stats["errors"]:
        print("\n⚠️  错误 (前5条):")
        for err in stats["errors"][:5]:
            print(f"   {err}")

    # 分类统计
    income = [t for t in transactions if t.direction == TransactionDirection.INCOME]
    expense = [t for t in transactions if t.direction == TransactionDirection.EXPENSE]
    neutral = [t for t in transactions if t.direction == TransactionDirection.NEUTRAL]

    print("\n💰 收支统计:")
    print(f"   收入: {len(income)} 笔, 共 {sum(t.amount for t in income):.2f} 元")
    print(f"   支出: {len(expense)} 笔, 共 {sum(t.amount for t in expense):.2f} 元")
    print(f"   不计收支: {len(neutral)} 笔")

    print("\n📝 示例记录 (前5条支出):")
    for t in expense[:5]:
        print(
            f"   {t.transaction_time.strftime('%Y-%m-%d')} | ¥{t.amount:>8} | {t.counterparty[:15]:<15} | {t.description[:20]}"
        )


def test_wechat():
    """测试微信解析"""
    file_path = (
        Path(__file__).parent.parent / "微信支付账单流水文件(20260101-20260407)_20260407142104.xlsx"
    )
    if not file_path.exists():
        print(f"❌ 微信文件不存在: {file_path}")
        return

    print("\n" + "=" * 60)
    print("微信账单解析测试")
    print("=" * 60)

    transactions, stats = parse_file(file_path)

    print("\n📊 统计:")
    print(f"   总行数: {stats['total']}")
    print(f"   成功: {stats['success']}")
    print(f"   失败: {stats['failed']}")

    if stats["errors"]:
        print("\n⚠️  错误 (前5条):")
        for err in stats["errors"][:5]:
            print(f"   {err}")

    # 分类统计
    income = [t for t in transactions if t.direction == TransactionDirection.INCOME]
    expense = [t for t in transactions if t.direction == TransactionDirection.EXPENSE]
    neutral = [t for t in transactions if t.direction == TransactionDirection.NEUTRAL]

    print("\n💰 收支统计:")
    print(f"   收入: {len(income)} 笔, 共 {sum(t.amount for t in income):.2f} 元")
    print(f"   支出: {len(expense)} 笔, 共 {sum(t.amount for t in expense):.2f} 元")
    print(f"   中性交易: {len(neutral)} 笔")

    print("\n📝 示例记录 (前5条支出):")
    for t in expense[:5]:
        desc = t.description[:20] if t.description else ""
        print(
            f"   {t.transaction_time.strftime('%Y-%m-%d')} | ¥{t.amount:>8} | {t.counterparty[:15]:<15} | {desc}"
        )


if __name__ == "__main__":
    test_alipay()
    test_wechat()
