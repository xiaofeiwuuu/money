"""管理 API"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import get_current_admin, get_current_user
from ..db.models import User
from ..services.parser_config import (
    add_alias,
    get_all_configs,
    load_parser_config,
    update_cache,
    update_config,
)

router = APIRouter()


class ParserConfigResponse(BaseModel):
    id: str
    source: str
    field_name: str
    column_aliases: List[str]
    is_required: bool
    description: Optional[str]
    updated_at: str


class UpdateAliasesRequest(BaseModel):
    source: str  # alipay/wechat
    field_name: str  # transaction_time, amount, etc.
    column_aliases: List[str]


class AddAliasRequest(BaseModel):
    source: str
    field_name: str
    new_alias: str


@router.get("/parser-configs", response_model=List[ParserConfigResponse])
async def list_parser_configs(
    source: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取解析器配置列表

    可选按来源筛选：alipay 或 wechat
    """
    return await get_all_configs(db, source=source)


@router.put("/parser-configs")
async def update_parser_config(
    request: UpdateAliasesRequest,
    current_user: User = Depends(get_current_admin),  # 需要管理员权限
    db: AsyncSession = Depends(get_db),
):
    """
    更新解析器配置（替换所有别名）

    示例：将支付宝的 transaction_time 字段的别名更新为 ["交易时间", "时间", "创建时间"]
    """
    success = await update_config(
        db,
        source=request.source,
        field_name=request.field_name,
        column_aliases=request.column_aliases,
    )

    if not success:
        raise HTTPException(status_code=404, detail="配置不存在")

    # 刷新缓存
    aliases = await load_parser_config(db, request.source)
    update_cache(request.source, aliases)

    return {"success": True, "message": "配置已更新"}


@router.post("/parser-configs/add-alias")
async def add_column_alias(
    request: AddAliasRequest,
    current_user: User = Depends(get_current_admin),  # 需要管理员权限
    db: AsyncSession = Depends(get_db),
):
    """
    添加新的列名别名

    当发现新的列名格式时，可以直接添加别名而不影响现有配置
    """
    success = await add_alias(
        db,
        source=request.source,
        field_name=request.field_name,
        new_alias=request.new_alias,
    )

    if not success:
        raise HTTPException(status_code=404, detail="配置不存在")

    # 刷新缓存
    aliases = await load_parser_config(db, request.source)
    update_cache(request.source, aliases)

    return {"success": True, "message": f"已添加别名: {request.new_alias}"}


@router.post("/parser-configs/reload")
async def reload_parser_configs(
    current_user: User = Depends(get_current_admin),  # 需要管理员权限
    db: AsyncSession = Depends(get_db),
):
    """
    重新加载解析器配置到缓存

    修改数据库后调用此接口使配置生效
    """
    for source in ["alipay", "wechat"]:
        aliases = await load_parser_config(db, source)
        update_cache(source, aliases)

    return {"success": True, "message": "配置已重新加载"}
