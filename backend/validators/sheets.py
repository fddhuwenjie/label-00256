"""
企业微信表格数据验证模型
定义表格操作的请求和响应 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum
from .common import ResponseBase


class CellPosition(BaseModel):
    """单元格位置"""
    row: int = Field(..., ge=1, description="行号，从1开始")
    col: int = Field(..., ge=1, description="列号，从1开始")


class CellRange(BaseModel):
    """单元格范围"""
    start_row: int = Field(..., ge=1, description="起始行")
    start_col: int = Field(..., ge=1, description="起始列")
    end_row: int = Field(..., ge=1, description="结束行")
    end_col: int = Field(..., ge=1, description="结束列")


class CellData(BaseModel):
    """单元格数据"""
    row: int = Field(..., ge=1, description="行号，从1开始")
    col: int = Field(..., ge=1, description="列号，从1开始")
    value: Any


class WriteRequest(BaseModel):
    """写入请求"""
    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID")
    data: List[CellData] = Field(..., description="要写入的数据")


class WriteResponse(ResponseBase):
    """写入响应"""
    updated_cells: int = 0


class ReadRequest(BaseModel):
    """读取请求"""
    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID")


class ReadCellRequest(BaseModel):
    """读取单元格请求"""
    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID")
    row: int = Field(..., ge=1, description="行号")
    col: int = Field(..., ge=1, description="列号")


class ReadRangeRequest(BaseModel):
    """读取范围请求"""
    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID")
    range: CellRange = Field(..., description="读取范围")


class QueryOperator(str, Enum):
    """查询操作符"""
    EQ = "eq"       # 等于
    NE = "ne"       # 不等于
    GT = "gt"       # 大于
    GE = "ge"       # 大于等于
    LT = "lt"       # 小于
    LE = "le"       # 小于等于
    CONTAINS = "contains"  # 包含
    STARTS_WITH = "starts_with"  # 开头
    ENDS_WITH = "ends_with"  # 结尾


class QueryCondition(BaseModel):
    """查询条件"""
    col: int = Field(..., ge=1, description="列号")
    operator: QueryOperator = Field(..., description="操作符")
    value: Any = Field(..., description="比较值")


class QueryRequest(BaseModel):
    """条件查询请求"""
    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID")
    conditions: List[QueryCondition] = Field(..., description="查询条件")
    logic: str = Field("and", description="条件逻辑: and/or")


class ReadResponse(ResponseBase):
    """读取响应"""
    data: List[List[Any]] = Field(default_factory=list, description="表格数据")
    rows: int = 0
    cols: int = 0


class CellResponse(ResponseBase):
    """单元格响应"""
    value: Any = None
    row: int = 0
    col: int = 0
