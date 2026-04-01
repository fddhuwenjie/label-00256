"""
本地 Excel 文件操作 API 路由
只负责请求分发和响应组装，业务逻辑委托给 service 层
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse

from core.auth import require_permission, Permission, APIKeyInfo
from core.logger import logger
from core.dependencies import get_local_excel_service
from validators.local_excel import ExportRequest
from services.local_excel import LocalExcelService


router = APIRouter(prefix="/local", tags=["本地Excel操作"])


@router.post("/upload", summary="上传 xlsx 文件")
async def upload_excel(
    file: UploadFile = File(...),
    key_info: APIKeyInfo = Depends(require_permission(Permission.LOCAL_FILE)),
    service: LocalExcelService = Depends(get_local_excel_service)
):
    """
    上传本地 xlsx 文件并解析

    Args:
        file: xlsx 文件
        key_info: API 密钥认证信息
        service: 本地 Excel 服务实例

    Returns:
        包含成功状态、文件信息和消息的响应字典

    Raises:
        HTTPException: 文件格式不支持或解析失败
    """
    content = await file.read()

    try:
        result = service.upload_file(content, file.filename)
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
    sheet_name: str = None,
    range: str = None,
    key_info: APIKeyInfo = Depends(require_permission(Permission.READ)),
    service: LocalExcelService = Depends(get_local_excel_service)
):
    """
    读取已上传的 xlsx 文件内容

    Args:
        file_id: 文件 ID（上传时返回）
        sheet_name: 工作表名称（可选）
        range: 读取范围，如 "A1:C10"（可选）
        key_info: API 密钥认证信息
        service: 本地 Excel 服务实例

    Returns:
        包含成功状态、表格数据和消息的响应字典

    Raises:
        HTTPException: 文件不存在或读取失败
    """
    try:
        result = service.read_file(file_id, sheet_name, range)
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
    key_info: APIKeyInfo = Depends(require_permission(Permission.LOCAL_FILE)),
    service: LocalExcelService = Depends(get_local_excel_service)
):
    """
    将数据导出为 xlsx 文件

    Args:
        request: 导出请求参数，包含 data、filename 和 sheet_name
        key_info: API 密钥认证信息
        service: 本地 Excel 服务实例

    Returns:
        包含成功状态、文件信息和消息的响应字典

    Raises:
        HTTPException: 导出失败
    """
    try:
        result = service.export_to_file(
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
    key_info: APIKeyInfo = Depends(require_permission(Permission.READ)),
    service: LocalExcelService = Depends(get_local_excel_service)
):
    """
    下载导出的 xlsx 文件

    Args:
        file_id: 文件 ID（导出时返回）
        key_info: API 密钥认证信息
        service: 本地 Excel 服务实例

    Returns:
        FileResponse 文件响应

    Raises:
        HTTPException: 文件不存在
    """
    file_path = service.get_export_file_path(file_id)

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
    key_info: APIKeyInfo = Depends(require_permission(Permission.LOCAL_FILE)),
    service: LocalExcelService = Depends(get_local_excel_service)
):
    """
    删除已上传或导出的文件

    Args:
        file_id: 文件 ID
        key_info: API 密钥认证信息
        service: 本地 Excel 服务实例

    Returns:
        包含成功状态和消息的响应字典

    Raises:
        HTTPException: 文件不存在
    """
    success = service.delete_file(file_id)

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
    key_info: APIKeyInfo = Depends(require_permission(Permission.READ)),
    service: LocalExcelService = Depends(get_local_excel_service)
):
    """
    列出所有已上传和导出的文件

    Args:
        key_info: API 密钥认证信息
        service: 本地 Excel 服务实例

    Returns:
        包含成功状态和文件列表的响应字典
    """
    result = service.list_files()
    return {
        "success": True,
        "data": result
    }
