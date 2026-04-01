"""
API路由 - 表格操作
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from core.auth import verify_api_key, require_permission, Permission, APIKeyInfo
from core.logger import logger
from core.exceptions import raise_bad_request
from validators.sheets import (
    WriteRequest, WriteResponse,
    ReadResponse, CellResponse,
    QueryRequest, CellRange
)
from services.sheet_service import SheetService
from services.dependencies import get_sheet_service

router = APIRouter(prefix="/api/v1/sheets", tags=["表格操作"])


@router.post("/write", response_model=WriteResponse, summary="写入数据到表格")
async def write_data(
    request: WriteRequest,
    sheet_service: SheetService = Depends(get_sheet_service),
    key_info: APIKeyInfo = Depends(require_permission(Permission.WRITE))
):
    """
    写入数据到企业微信在线表格
    
    Args:
        request: 写入请求数据
        sheet_service: 表格服务实例（依赖注入）
        key_info: API Key 信息（权限验证）
        
    Returns:
        WriteResponse: 写入响应
    """
    logger.info(f"写入请求: spreadsheet_id={request.spreadsheet_id}, cells={len(request.data)}")
    
    if not request.data:
        raise_bad_request("数据不能为空")
    
    updated = await sheet_service.write_data(
        request.spreadsheet_id,
        request.sheet_id,
        request.data
    )
    
    return WriteResponse(
        success=True,
        message=f"成功写入 {updated} 个单元格",
        updated_cells=updated
    )


@router.get("/read", response_model=ReadResponse, summary="读取表格全部数据")
async def read_data(
    spreadsheet_id: str = Query(..., description="表格ID"),
    sheet_id: Optional[str] = Query(None, description="工作表ID"),
    sheet_service: SheetService = Depends(get_sheet_service),
    key_info: APIKeyInfo = Depends(require_permission(Permission.READ))
):
    """
    读取企业微信在线表格的全部数据
    
    Args:
        spreadsheet_id: 表格ID
        sheet_id: 工作表ID（可选，默认第一个工作表）
        sheet_service: 表格服务实例（依赖注入）
        key_info: API Key 信息（权限验证）
        
    Returns:
        ReadResponse: 读取响应
    """
    logger.info(f"读取请求: spreadsheet_id={spreadsheet_id}")
    
    data = await sheet_service.read_all(spreadsheet_id, sheet_id)
    
    rows = len(data)
    cols = max(len(row) for row in data) if data else 0
    
    return ReadResponse(
        success=True,
        message="读取成功",
        data=data,
        rows=rows,
        cols=cols
    )


@router.get("/cell", response_model=CellResponse, summary="读取指定单元格")
async def read_cell(
    spreadsheet_id: str = Query(..., description="表格ID"),
    row: int = Query(..., ge=1, description="行号（从1开始）"),
    col: int = Query(..., ge=1, description="列号（从1开始）"),
    sheet_id: Optional[str] = Query(None, description="工作表ID"),
    sheet_service: SheetService = Depends(get_sheet_service),
    key_info: APIKeyInfo = Depends(require_permission(Permission.READ))
):
    """
    读取指定单元格的值
    
    Args:
        spreadsheet_id: 表格ID
        row: 行号（从1开始）
        col: 列号（从1开始）
        sheet_id: 工作表ID（可选）
        sheet_service: 表格服务实例（依赖注入）
        key_info: API Key 信息（权限验证）
        
    Returns:
        CellResponse: 单元格响应
    """
    logger.info(f"读取单元格: spreadsheet_id={spreadsheet_id}, row={row}, col={col}")
    
    value = await sheet_service.read_cell(spreadsheet_id, sheet_id, row, col)
    
    return CellResponse(
        success=True,
        message="读取成功",
        value=value,
        row=row,
        col=col
    )


@router.get("/range", response_model=ReadResponse, summary="读取指定范围")
async def read_range(
    spreadsheet_id: str = Query(..., description="表格ID"),
    start_row: int = Query(..., ge=1, description="起始行"),
    start_col: int = Query(..., ge=1, description="起始列"),
    end_row: int = Query(..., ge=1, description="结束行"),
    end_col: int = Query(..., ge=1, description="结束列"),
    sheet_id: Optional[str] = Query(None, description="工作表ID"),
    sheet_service: SheetService = Depends(get_sheet_service),
    key_info: APIKeyInfo = Depends(require_permission(Permission.READ))
):
    """
    读取指定范围的数据
    
    Args:
        spreadsheet_id: 表格ID
        start_row: 起始行
        start_col: 起始列
        end_row: 结束行
        end_col: 结束列
        sheet_id: 工作表ID（可选）
        sheet_service: 表格服务实例（依赖注入）
        key_info: API Key 信息（权限验证）
        
    Returns:
        ReadResponse: 读取响应
    """
    logger.info(f"读取范围: spreadsheet_id={spreadsheet_id}, range=[{start_row},{start_col}]-[{end_row},{end_col}]")
    
    if start_row > end_row or start_col > end_col:
        raise_bad_request("起始位置不能大于结束位置")
    
    data = await sheet_service.read_range(
        spreadsheet_id, sheet_id,
        start_row, start_col, end_row, end_col
    )
    
    rows = len(data)
    cols = max(len(row) for row in data) if data else 0
    
    return ReadResponse(
        success=True,
        message="读取成功",
        data=data,
        rows=rows,
        cols=cols
    )


@router.post("/query", response_model=ReadResponse, summary="条件查询")
async def query_data(
    request: QueryRequest,
    sheet_service: SheetService = Depends(get_sheet_service),
    key_info: APIKeyInfo = Depends(require_permission(Permission.READ))
):
    """
    根据条件查询表格数据
    
    Args:
        request: 查询请求数据
        sheet_service: 表格服务实例（依赖注入）
        key_info: API Key 信息（权限验证）
        
    Returns:
        ReadResponse: 查询响应
    """
    logger.info(f"条件查询: spreadsheet_id={request.spreadsheet_id}, conditions={len(request.conditions)}")
    
    if not request.conditions:
        raise_bad_request("查询条件不能为空")
    
    data = await sheet_service.query(
        request.spreadsheet_id,
        request.sheet_id,
        request.conditions,
        request.logic
    )
    
    rows = len(data)
    cols = max(len(row) for row in data) if data else 0
    
    return ReadResponse(
        success=True,
        message=f"查询到 {rows - 1 if rows > 0 else 0} 条记录",
        data=data,
        rows=rows,
        cols=cols
    )
