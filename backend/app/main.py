"""FastAPI 主应用"""
import logging
import sys

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .api import upload, auth, transactions, admin
from .core.config import get_settings
from .core.database import get_db

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

settings = get_settings()
logger.info(f"Starting {settings.APP_NAME} (DEBUG={settings.DEBUG})")

app = FastAPI(
    title="Money Manager API",
    description="个人/家庭收支管理系统",
    version="0.1.0",
)

# CORS 配置 - 从配置读取，不再硬编码
cors_origins = settings.get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True if cors_origins != ["*"] else False,  # * 时不能用 credentials
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(upload.router, prefix="/api", tags=["上传"])
app.include_router(transactions.router, prefix="/api", tags=["交易"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理"])


@app.get("/")
async def root():
    return {"message": "Money Manager API", "version": "0.1.0"}


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    """健康检查（含数据库连接）"""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "degraded", "database": "disconnected", "error": str(e)}
