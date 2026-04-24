"""解析器配置 - 轻量级模块，无数据库依赖"""

from typing import Dict, List

# 默认配置（硬编码回退）
DEFAULT_ALIPAY_ALIASES: Dict[str, List[str]] = {
    "transaction_time": ["交易时间", "交易创建时间", "创建时间", "时间"],
    "amount": ["金额", "金额(元)", "交易金额", "金额（元）"],
    "direction": ["收/支", "收/付款", "资金状态", "收支"],
    "counterparty": ["交易对方", "对方", "对方户名"],
    "description": ["商品说明", "商品名称", "商品", "备注"],
    "category": ["交易分类", "分类", "交易类型"],
    "order_id": ["交易订单号", "订单号", "交易号"],
    "payment_method": ["收/付款方式", "支付方式", "付款方式"],
    "status": ["交易状态", "状态"],
    "merchant_order_id": ["商家订单号", "商户订单号"],
    "note": ["备注", "说明"],
}

DEFAULT_WECHAT_ALIASES: Dict[str, List[str]] = {
    "transaction_time": ["交易时间", "时间", "创建时间"],
    "amount": ["金额(元)", "金额", "金额（元）", "交易金额"],
    "direction": ["收/支", "收支", "资金状态"],
    "counterparty": ["交易对方", "对方", "对方户名"],
    "description": ["商品", "商品说明", "商品名称", "备注"],
    "category": ["交易类型", "类型", "交易分类"],
    "order_id": ["交易单号", "订单号", "交易号"],
    "payment_method": ["支付方式", "付款方式", "收/付款方式"],
    "status": ["当前状态", "状态", "交易状态"],
    "merchant_order_id": ["商户单号", "商家订单号", "商户订单号"],
    "note": ["备注", "说明"],
}

# 内存缓存（可被数据库配置覆盖）
_config_cache: Dict[str, Dict[str, List[str]]] = {}


def get_default_aliases(source: str) -> Dict[str, List[str]]:
    """获取默认别名配置"""
    if source == "alipay":
        return DEFAULT_ALIPAY_ALIASES.copy()
    elif source == "wechat":
        return DEFAULT_WECHAT_ALIASES.copy()
    return {}


def get_cached_aliases(source: str) -> Dict[str, List[str]]:
    """
    获取缓存的别名配置（返回副本，防止污染缓存）

    优先返回缓存（来自数据库），否则返回默认配置
    """
    if source in _config_cache:
        return _config_cache[source].copy()
    return get_default_aliases(source)


def update_cache(source: str, aliases: Dict[str, List[str]]):
    """更新缓存（由数据库服务调用）"""
    _config_cache[source] = aliases


def clear_cache():
    """清除缓存"""
    _config_cache.clear()
