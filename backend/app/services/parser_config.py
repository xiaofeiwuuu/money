"""解析器配置服务 - 数据库操作"""

import json
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import ParserConfig
from ..parsers.config import (
    clear_cache,
    get_cached_aliases,
    get_default_aliases,
    update_cache,
)

# 重新导出以保持兼容
__all__ = [
    "add_alias",
    "clear_cache",
    "get_all_configs",
    "get_cached_aliases",
    "get_default_aliases",
    "load_parser_config",
    "update_cache",
    "update_config",
]


async def load_parser_config(db: AsyncSession, source: str) -> Dict[str, List[str]]:
    """从数据库加载解析器配置（DB 覆盖默认值，而非替换）"""
    # 先加载默认配置
    aliases = get_default_aliases(source)

    # 用数据库配置覆盖
    result = await db.execute(select(ParserConfig).where(ParserConfig.source == source))
    configs = result.scalars().all()

    for config in configs:
        try:
            aliases[config.field_name] = json.loads(config.column_aliases)
        except json.JSONDecodeError:
            aliases[config.field_name] = [config.column_aliases]

    return aliases


async def get_all_configs(db: AsyncSession, source: Optional[str] = None) -> List[dict]:
    """获取所有配置"""
    query = select(ParserConfig)
    if source:
        query = query.where(ParserConfig.source == source)
    query = query.order_by(ParserConfig.source, ParserConfig.field_name)

    result = await db.execute(query)
    configs = result.scalars().all()

    return [
        {
            "id": str(c.id),
            "source": c.source,
            "field_name": c.field_name,
            "column_aliases": json.loads(c.column_aliases),
            "is_required": c.is_required,
            "description": c.description,
            "updated_at": c.updated_at.isoformat(),
        }
        for c in configs
    ]


async def update_config(
    db: AsyncSession,
    source: str,
    field_name: str,
    column_aliases: List[str],
) -> bool:
    """更新配置"""
    result = await db.execute(
        select(ParserConfig).where(
            ParserConfig.source == source,
            ParserConfig.field_name == field_name,
        )
    )
    config = result.scalar_one_or_none()

    if config:
        config.column_aliases = json.dumps(column_aliases, ensure_ascii=False)
        await db.commit()
        clear_cache()
        return True
    return False


async def add_alias(
    db: AsyncSession,
    source: str,
    field_name: str,
    new_alias: str,
) -> bool:
    """添加新的列名别名"""
    result = await db.execute(
        select(ParserConfig).where(
            ParserConfig.source == source,
            ParserConfig.field_name == field_name,
        )
    )
    config = result.scalar_one_or_none()

    if config:
        aliases = json.loads(config.column_aliases)
        if new_alias not in aliases:
            aliases.append(new_alias)
            config.column_aliases = json.dumps(aliases, ensure_ascii=False)
            await db.commit()
            clear_cache()
        return True
    return False
