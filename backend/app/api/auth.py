"""认证 API"""

import logging
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..core.database import get_db
from ..core.security import (
    create_access_token,
    get_current_user,
    get_password_hash_async,
    verify_password_async,
)
from ..db.models import User

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    nickname: str
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class UpdateUserRequest(BaseModel):
    """更新用户请求"""

    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    # 异步哈希密码（避免阻塞事件循环）
    hashed_password = await get_password_hash_async(user_data.password)

    # 直接插入，catch 唯一约束冲突（避免 race condition）
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        nickname=user_data.nickname,
    )
    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
        logger.info(f"用户注册成功: user_id={user.id}")
    except IntegrityError:
        await db.rollback()
        logger.warning("注册失败: 邮箱已存在")
        raise HTTPException(status_code=400, detail="邮箱已被注册") from None

    # 生成 token
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    # 统一日志消息，防止账号枚举攻击
    if not user:
        logger.warning("登录失败: 凭证无效")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
        )

    # 异步验证密码（避免阻塞事件循环）
    if not await verify_password_async(user_data.password, user.hashed_password):
        logger.warning("登录失败: 凭证无效")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
        )

    if not user.is_active:
        logger.warning("登录失败: 账户已禁用")
        raise HTTPException(status_code=400, detail="用户已被禁用")

    logger.info(f"用户登录成功: user_id={user.id}")
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url,
    )


@router.put("/me", response_model=UserResponse)
async def update_me(
    request: UpdateUserRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前用户信息"""
    if request.nickname is not None:
        current_user.nickname = request.nickname
    if request.avatar_url is not None:
        current_user.avatar_url = request.avatar_url

    await db.commit()
    await db.refresh(current_user)

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url,
    )
