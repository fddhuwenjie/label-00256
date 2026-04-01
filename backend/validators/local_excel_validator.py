"""
本地 Excel 操作 Schema 定义
包含本地上传、读取、导出 Excel 文件相关的请求和响应模型
"""
from pydantic import BaseModel, Field
from typing import List, Any, Optional, Dict


class ExportRequest(BaseModel):
    """导出 Excel 请求

    将数据导出为 xlsx 文件的请求参数
    """

    data: List[List[Any]] = Field(..., description="二维数组数据")
    filename: Optional[str] = Field(None, description="导出文件名，可选")
    sheet_name: str = Field("Sheet1", description="工作表名称，默认 Sheet1")


class ReadRequest(BaseModel):
    """读取本地 Excel 请求

    读取已上传 xlsx 文件的请求参数
    """

    file_id: str = Field(..., description="文件ID（上传时返回）")
    sheet_name: Optional[str] = Field(None, description="工作表名称，可选")
    range: Optional[str] = Field(None, description="读取范围，如 A1:C10，可选")


class FileInfo(BaseModel):
    """文件基础信息"""

    file_id: str = Field(..., description="文件ID")
    filename: str = Field(..., description="文件名")


class FileUploadResponse(BaseModel):
    """文件上传响应

    上传 xlsx 文件后的返回结果
    """

    file_id: str = Field(..., description="文件ID")
    filename: str = Field(..., description="文件名")
    sheets: List[str] = Field(..., description="工作表名称列表")
    row_count: int = Field(..., description="总行数")
    column_count: int = Field(..., description="总列数")


class FileReadResponse(BaseModel):
    """文件读取响应

    读取本地 xlsx 文件的返回结果
    """

    file_id: str = Field(..., description="文件ID")
    sheet_name: str = Field(..., description="工作表名称")
    range: str = Field(..., description="读取范围")
    values: List[List[Any]] = Field(..., description="二维表格数据")
    row_count: int = Field(..., description="读取的行数")
    column_count: int = Field(..., description="读取的列数")


class FileExportResponse(BaseModel):
    """文件导出响应

    导出 xlsx 文件后的返回结果
    """

    file_id: str = Field(..., description="文件ID，用于下载")
    filename: str = Field(..., description="文件名")
    path: str = Field(..., description="文件存储路径")
    row_count: int = Field(..., description="导出的行数")
    column_count: int = Field(..., description="导出的列数")


class FileListResponse(BaseModel):
    """文件列表响应

    列出所有已上传和导出的文件
    """

    uploads: List[Dict[str, Any]] = Field(..., description="已上传文件列表")
    exports: List[Dict[str, Any]] = Field(..., description="已导出文件列表")
