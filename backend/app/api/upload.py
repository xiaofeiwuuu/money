"""上传 API"""

import logging
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import get_current_user
from ..db.models import User
from ..parsers.parser import detect_source, parse_file
from ..services.transaction import save_transactions

logger = logging.getLogger(__name__)
router = APIRouter()

# 文件大小限制 (20MB)
MAX_FILE_SIZE = 20 * 1024 * 1024


class UploadResponse(BaseModel):
    """上传响应"""

    success: bool
    message: str
    stats: dict
    transactions: list


class SaveResponse(BaseModel):
    """保存响应"""

    success: bool
    message: str
    saved: int
    duplicates: int
    failed: int


async def validate_upload_file(file: UploadFile) -> bytes:
    """验证并读取上传文件"""
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()

    if suffix not in [".csv", ".xlsx"]:
        raise HTTPException(
            status_code=400, detail=f"不支持的文件类型: {suffix}，仅支持 .csv 和 .xlsx"
        )

    # 读取并检查大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, detail=f"文件过大，最大支持 {MAX_FILE_SIZE // 1024 // 1024}MB"
        )

    return content


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    source: Optional[str] = None,
    current_user: User = Depends(get_current_user),  # 需要登录
):
    """
    上传账单文件（支付宝 CSV 或微信 XLSX）- 仅解析预览

    需要登录。文件大小限制 20MB。
    """
    content = await validate_upload_file(file)
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        # detect_source 对 .csv/.xlsx 总能返回结果（有扩展名兜底）
        if source is None:
            source = detect_source(Path(filename))

        transactions, stats = parse_file(tmp_path, source=source)
        logger.info(f"解析成功: [文件已上传], {stats['success']} 条记录")

        return UploadResponse(
            success=True,
            message=f"成功解析 {stats['success']} 条记录",
            stats=stats,
            transactions=[t.to_dict() for t in transactions],
        )

    except Exception as e:
        logger.exception("解析失败")
        raise HTTPException(status_code=400, detail=str(e)) from e

    finally:
        tmp_path.unlink(missing_ok=True)


@router.post("/upload/save", response_model=SaveResponse)
async def upload_and_save(
    file: UploadFile = File(...),
    source: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    上传账单文件并保存到数据库（需要登录）

    自动去重：相同来源+订单号的记录不会重复导入
    文件大小限制 20MB。
    """
    content = await validate_upload_file(file)
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        # detect_source 对 .csv/.xlsx 总能返回结果（有扩展名兜底）
        if source is None:
            source = detect_source(Path(filename))

        transactions, _ = parse_file(tmp_path, source=source)

        saved, duplicates, failed = await save_transactions(
            db, current_user.id, transactions, filename
        )
        logger.info(
            f"导入成功: user={current_user.id}, 新增={saved}, 重复={duplicates}, 失败={failed}"
        )

        return SaveResponse(
            success=True,
            message=f"导入完成：新增 {saved} 条，跳过 {duplicates} 条重复记录",
            saved=saved,
            duplicates=duplicates,
            failed=failed,
        )

    except Exception as e:
        logger.exception("导入失败")
        raise HTTPException(status_code=400, detail=str(e)) from e

    finally:
        tmp_path.unlink(missing_ok=True)


@router.post("/upload/preview")
async def preview_upload(
    file: UploadFile = File(...),
    limit: int = 10,
    current_user: User = Depends(get_current_user),  # 需要登录
):
    """
    预览上传文件（仅返回前 N 条）

    需要登录。用于上传前预览，不会存入数据库。
    """
    content = await validate_upload_file(file)
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        source = detect_source(Path(filename))
        transactions, stats = parse_file(tmp_path, source=source)
        logger.info(f"预览成功: user={current_user.id}, source={source}, total={stats['total']}")

        return {
            "source": source,
            "total": stats["total"],
            "preview": [t.to_dict() for t in transactions[:limit]],
        }

    except Exception as e:
        logger.exception("预览失败")
        raise HTTPException(status_code=400, detail=str(e)) from e

    finally:
        tmp_path.unlink(missing_ok=True)
