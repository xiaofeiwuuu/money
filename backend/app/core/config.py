"""应用配置"""
import logging
from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache

logger = logging.getLogger(__name__)

# 开发模式专用密钥（固定值，重启后 token 仍有效）
_DEV_SECRET_KEY = "dev-only-secret-key-do-not-use-in-production-12345"


class Settings(BaseSettings):
    """应用设置"""
    # 数据库
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/money"

    # JWT - 无默认值，必须配置
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # 应用
    APP_NAME: str = "Money Manager"
    DEBUG: bool = True

    # CORS - 生产环境需要配置具体域名
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        """验证 SECRET_KEY 配置"""
        if not self.SECRET_KEY:
            if self.DEBUG:
                # 开发模式使用固定密钥，重启后 token 仍有效
                object.__setattr__(self, "SECRET_KEY", _DEV_SECRET_KEY)
                logger.warning(
                    "SECRET_KEY not configured, using dev-only key. "
                    "Set SECRET_KEY in .env for production!"
                )
            else:
                raise ValueError(
                    "SECRET_KEY is required in production. "
                    "Set it in .env file or environment variable."
                )
        return self

    def get_cors_origins(self) -> list[str]:
        """获取 CORS 允许的源列表"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
