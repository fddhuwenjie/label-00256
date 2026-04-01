"""
基础 Schema 定义
包含所有请求响应的通用基类
"""
from pydantic import BaseModel, Field
from typing import Optional


class ResponseBase(BaseModel):
    """响应基类

    所有 API 响应的基础模型，包含通用字段
    """

    success: bool = Field(True, description="操作是否成功")
    message: str = Field("ok", description="响应消息")


class ErrorResponse(BaseModel):
    """错误响应

    API 错误响应的标准格式
    """

    success: bool = Field(False, description="操作是否成功")
    message: str = Field(..., description="错误消息")
    error_code: Optional[str] = Field(None, description="错误代码")


class HealthResponse(BaseModel):
    """健康检查响应

    服务健康状态检查的响应模型
    """

    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="版本号")
    mode: str = Field(..., description="运行模式：mock/production")
    timestamp: str = Field(..., description="当前时间戳")
    services: dict = Field(..., description="各服务状态")
