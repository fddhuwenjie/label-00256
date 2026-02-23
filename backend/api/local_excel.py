"""
本地 Excel 文件操作 API
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from typing import List, Any, Optional
from pydantic import BaseModel

from core.auth import require_permission, Permission, APIKeyInfo
from core.logger import logger
from services.local_excel import local_excel_service


router = APIRouter(prefix="/local", tags=["本地Excel操作"])


class ExportRequest(BaseModel):
    """导出请求"""
    data: List[List[Any]]
    filename: Optional[str] = None
    sheet_name: str = "Sheet1"


class ReadRequest(BaseModel):
    """读取请求"""
    file_id: str
    sheet_name: Optional[str] = None
    range: Optional[str] = None


@router.post("/upload", summary="上传 xlsx 文件")
async def upload_excel(
    file: UploadFile = File(...),
    key_info: APIKeyInfo = Depends(require_permission(Permission.LOCAL_FILE))
):
    """
    上传本地 xlsx 文件并解析
    
    - **file**: xlsx 文件
    
    返回文件信息，包括工作表列表、行列数等
    """
    if not file.filename.lower().endswith('.xlsx'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": "仅支持 .xlsx 格式文件"}
        )
    
    content = await file.read()
    
    try:
        result = local_excel_service.upload_file(content, file.filename)
        return {
            "success": True,
            "data": result,
            "message": "文件上传成功"
        }
    except Exception as e:
        logger.error(f"上传文件失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": str(e)}
        )


@router.get("/read/{file_id}", summary="读取已上传的 xlsx 文件")
async def read_excel(
    file_id: str,
    sheet_name: Optional[str] = None,
    range: Optional[str] = None,
    key_info: APIKeyInfo = Depends(require_permission(Permission.READ))
):
    """
    读取已上传的 xlsx 文件内容
    
    - **file_id**: 文件 ID（上传时返回）
    - **sheet_name**: 工作表名称（可选）
    - **range**: 读取范围，如 "A1:C10"（可选）
    """
    try:
        result = local_excel_service.read_file(file_id, sheet_name, range)
        return {
            "success": True,
            "data": result,
            "message": "读取成功"
        }
    except Exception as e:
        logger.error(f"读取文件失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": str(e)}
        )


@router.post("/export", summary="导出数据为 xlsx 文件")
async def export_excel(
    request: ExportRequest,
    key_info: APIKeyInfo = Depends(require_permission(Permission.LOCAL_FILE))
):
    """
    将数据导出为 xlsx 文件
    
    - **data**: 二维数组数据
    - **filename**: 文件名（可选）
    - **sheet_name**: 工作表名称（默认 Sheet1）
    
    返回文件 ID，可用于下载
    """
    try:
        result = local_excel_service.export_to_file(
            request.data,
            request.filename,
            request.sheet_name
        )
        return {
            "success": True,
            "data": result,
            "message": "导出成功"
        }
    except Exception as e:
        logger.error(f"导出文件失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": str(e)}
        )


@router.get("/download/{file_id}", summary="下载导出的 xlsx 文件")
async def download_excel(
    file_id: str,
    key_info: APIKeyInfo = Depends(require_permission(Permission.READ))
):
    """
    下载导出的 xlsx 文件
    
    - **file_id**: 文件 ID（导出时返回）
    """
    file_path = local_excel_service.get_export_file_path(file_id)
    
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "文件不存在"}
        )
    
    return FileResponse(
        path=file_path,
        filename=f"{file_id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.delete("/{file_id}", summary="删除文件")
async def delete_excel(
    file_id: str,
    key_info: APIKeyInfo = Depends(require_permission(Permission.LOCAL_FILE))
):
    """
    删除已上传或导出的文件
    
    - **file_id**: 文件 ID
    """
    success = local_excel_service.delete_file(file_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "文件不存在"}
        )
    
    return {
        "success": True,
        "message": "文件已删除"
    }


@router.get("/files", summary="列出所有文件")
async def list_files(
    key_info: APIKeyInfo = Depends(require_permission(Permission.READ))
):
    """
    列出所有已上传和导出的文件
    """
    result = local_excel_service.list_files()
    return {
        "success": True,
        "data": result
    }
