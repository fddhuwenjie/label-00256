"""
表格操作数据校验模型
定义表格相关 API 的请求和响应 schema
"""
from typing import Optional, List, Any, Dict
from enum import Enum
from pydantic import BaseModel, Field


class ResponseBase(BaseModel):
    """
    响应基类
    
    Attributes:
        success: 操作是否成功
        message: 响应消息
    """
    success: bool = True
    message: str = "ok"


class ErrorResponse(BaseModel):
    """
    错误响应
    
    Attributes:
        success: 操作是否成功，固定为 False
        message: 错误消息
        error_code: 错误代码（可选）
    """
    success: bool = False
    message: str
    error_code: Optional[str] = None


class CellPosition(BaseModel):
    """
    单元格位置
    
    Attributes:
        row: 行号，从 1 开始
        col: 列号，从 1 开始
    """
    row: int = Field(..., ge=1, description="行号，从1开始")
    col: int = Field(..., ge=1, description="列号，从1开始")


class CellRange(BaseModel):
    """
    单元格范围
    
    Attributes:
        start_row: 起始行
        start_col: 起始列
        end_row: 结束行
        end_col: 结束列
    """
    start_row: int = Field(..., ge=1, description="起始行")
    start_col: int = Field(..., ge=1, description="起始列")
    end_row: int = Field(..., ge=1, description="结束行")
    end_col: int = Field(..., ge=1, description="结束列")


class CellData(BaseModel):
    """
    单元格数据
    
    Attributes:
        row: 行号，从 1 开始
        col: 列号，从 1 开始
        value: 单元格值
    """
    row: int = Field(..., ge=1, description="行号，从1开始")
    col: int = Field(..., ge=1, description="列号，从1开始")
    value: Any


class WriteRequest(BaseModel):
    """
    写入请求
    
    Attributes:
        spreadsheet_id: 表格 ID
        sheet_id: 工作表 ID（可选）
        data: 要写入的单元格数据列表
    """
    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID")
    data: List[CellData] = Field(..., description="要写入的数据")


class WriteResponse(ResponseBase):
    """
    写入响应
    
    Attributes:
        updated_cells: 成功更新的单元格数量
    """
    updated_cells: int = 0


class ReadRequest(BaseModel):
    """
    读取请求
    
    Attributes:
        spreadsheet_id: 表格 ID
        sheet_id: 工作表 ID（可选）
    """
    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID")


class ReadCellRequest(BaseModel):
    """
    读取单元格请求
    
    Attributes:
        spreadsheet_id: 表格 ID
        sheet_id: 工作表 ID（可选）
        row: 行号
        col: 列号
    """
    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID")
    row: int = Field(..., ge=1, description="行号")
    col: int = Field(..., ge=1, description="列号")


class ReadRangeRequest(BaseModel):
    """
    读取范围请求
    
    Attributes:
        spreadsheet_id: 表格 ID
        sheet_id: 工作表 ID（可选）
        range: 读取范围
    """
    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID")
    range: CellRange = Field(..., description="读取范围")


class QueryOperator(str, Enum):
    """
    查询操作符
    
    枚举值:
        EQ: 等于
        NE: 不等于
        GT: 大于
        GE: 大于等于
        LT: 小于
        LE: 小于等于
        CONTAINS: 包含
        STARTS_WITH: 开头匹配
        ENDS_WITH: 结尾匹配
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
    """
    查询条件
    
    Attributes:
        col: 列号
        operator: 比较操作符
        value: 比较值
    """
    col: int = Field(..., ge=1, description="列号")
    operator: QueryOperator = Field(..., description="操作符")
    value: Any = Field(..., description="比较值")


class QueryRequest(BaseModel):
    """
    条件查询请求
    
    Attributes:
        spreadsheet_id: 表格 ID
        sheet_id: 工作表 ID（可选）
        conditions: 查询条件列表
        logic: 条件逻辑，"and" 或 "or"，默认为 "and"
    """
    spreadsheet_id: str = Field(..., description="表格ID")
    sheet_id: Optional[str] = Field(None, description="工作表ID")
    conditions: List[QueryCondition] = Field(..., description="查询条件列表")
    logic: str = Field("and", description="条件逻辑: and/or")


class ReadResponse(ResponseBase):
    """
    读取响应
    
    Attributes:
        data: 二维数组形式的表格数据
        rows: 行数
        cols: 列数
    """
    data: List[List[Any]] = Field(default_factory=list, description="表格数据")
    rows: int = 0
    cols: int = 0


class CellResponse(ResponseBase):
    """
    单元格响应
    
    Attributes:
        value: 单元格值
        row: 行号
        col: 列号
    """
    value: Any = None
    row: int = 0
    col: int = 0


class HealthResponse(BaseModel):
    """
    健康检查响应
    
    Attributes:
        status: 服务状态
        version: 版本号
        mode: 运行模式
        timestamp: 时间戳
        services: 各服务状态
    """
    status: str = "healthy"
    version: str = "1.0.0"
    mode: str = "mock"
    timestamp: str = ""
    services: Dict[str, str] = Field(default_factory=dict)
