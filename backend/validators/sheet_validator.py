"""
表格操作 Schema 定义
包含企业微信表格读写相关的请求和响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum

from validators.base import ResponseBase


class CellPosition(BaseModel):
    """单元格位置

    表示单个单元格的行列坐标
    """

    row: int = Field(..., ge=1, description="行号，从1开始")
    col: int = Field(..., ge=1, description="列号，从1开始")


class CellRange(BaseModel):
    """单元格范围

    表示一个矩形区域的起止坐标
    """

    start_row: int = Field(..., ge=1, description="起始行")
    start_col: int = Field(..., ge=1, description="起始列")
    end_row: int = Field(..., ge=1, description="结束行")
    end_col: int = Field(..., ge=1, description="结束列")


class CellData(BaseModel):
    """单元格数据

    单个单元格的数据及其位置
    """

    row: int = Field(..., ge=1, description="行号，从1开始")
    col: int = Field(..., ge=1, description="列号，从1开始")
    value: Any = Field(..., description="单元格值")


class WriteRequest(BaseModel):
    """写入数据请求

    向表格写入数据的请求参数
    """

    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID，默认为第一个工作表")
    data: List[CellData] = Field(..., description="要写入的单元格数据列表")


class WriteResponse(ResponseBase):
    """写入数据响应

    写入操作的返回结果
    """

    updated_cells: int = Field(0, description="成功更新的单元格数量")


class ReadRequest(BaseModel):
    """读取全部数据请求

    读取表格全部数据的请求参数
    """

    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID，默认为第一个工作表")


class ReadCellRequest(BaseModel):
    """读取单元格请求

    读取单个单元格的请求参数
    """

    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID，默认为第一个工作表")
    row: int = Field(..., ge=1, description="行号")
    col: int = Field(..., ge=1, description="列号")


class ReadRangeRequest(BaseModel):
    """读取范围请求

    读取指定区域数据的请求参数
    """

    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID，默认为第一个工作表")
    range: CellRange = Field(..., description="读取范围")


class QueryOperator(str, Enum):
    """查询操作符

    条件查询支持的操作符类型
    """

    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GE = "ge"
    LT = "lt"
    LE = "le"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


class QueryCondition(BaseModel):
    """查询条件

    单个查询条件的定义
    """

    col: int = Field(..., ge=1, description="列号")
    operator: QueryOperator = Field(..., description="操作符")
    value: Any = Field(..., description="比较值")


class QueryRequest(BaseModel):
    """条件查询请求

    根据条件查询表格数据的请求参数
    """

    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID，默认为第一个工作表")
    conditions: List[QueryCondition] = Field(..., description="查询条件列表")
    logic: str = Field("and", description="条件逻辑: and/or")


class ReadResponse(ResponseBase):
    """读取数据响应

    读取表格数据的返回结果
    """

    data: List[List[Any]] = Field(default_factory=list, description="二维表格数据")
    rows: int = Field(0, description="总行数")
    cols: int = Field(0, description="总列数")


class CellResponse(ResponseBase):
    """单元格响应

    读取单个单元格的返回结果
    """

    value: Any = Field(None, description="单元格值")
    row: int = Field(0, description="行号")
    col: int = Field(0, description="列号")
