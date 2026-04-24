"""安全相关工具"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

import anyio
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_settings
from .database import get_db

settings = get_settings()
security = HTTPBearer()


def _verify_password_sync(plain_password: str, hashed_password: str) -> bool:
    """同步验证密码（内部使用）"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def _hash_password_sync(password: str) -> str:
    """同步生成密码哈希（内部使用）"""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    """异步验证密码（避免阻塞事件循环）"""
    return await anyio.to_thread.run_sync(_verify_password_sync, plain_password, hashed_password)


async def get_password_hash_async(password: str) -> str:
    """异步生成密码哈希（避免阻塞事件循环）"""
    return await anyio.to_thread.run_sync(_hash_password_sync, password)


# 同步版本保留给测试使用
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码（同步版本，仅用于测试）"""
    return _verify_password_sync(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希（同步版本，仅用于测试）"""
    return _hash_password_sync(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """解析 JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户"""
    from ..db.models import User

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")

    return user


async def get_current_admin(
    current_user=Depends(get_current_user),
):
    """获取当前管理员用户"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user
