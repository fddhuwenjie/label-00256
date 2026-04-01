"""
本地 Excel 数据验证模型
定义本地 Excel 操作的请求和响应 Schema
"""
from pydantic import BaseModel
from typing import List, Any, Optional


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
