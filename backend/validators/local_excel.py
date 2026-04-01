"""
本地 Excel 操作数据校验模型
定义本地 Excel 相关 API 的请求和响应 schema
"""
from typing import List, Any, Optional
from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    """
    导出请求参数校验模型
    
    Attributes:
        data: 二维数组数据
        filename: 导出文件名（可选）
        sheet_name: 工作表名称，默认为 "Sheet1"
    """
    data: List[List[Any]] = Field(..., description="二维数组数据")
    filename: Optional[str] = Field(None, description="导出文件名")
    sheet_name: str = Field("Sheet1", description="工作表名称")


class ReadRequest(BaseModel):
    """
    读取请求参数校验模型
    
    Attributes:
        file_id: 文件 ID
        sheet_name: 工作表名称（可选）
        range: 读取范围，如 "A1:C10"（可选）
    """
    file_id: str = Field(..., description="文件 ID")
    sheet_name: Optional[str] = Field(None, description="工作表名称")
    range: Optional[str] = Field(None, description="读取范围，如 A1:C10")
