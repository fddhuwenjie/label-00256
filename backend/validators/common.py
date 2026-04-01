"""
通用数据验证模型
定义通用的响应和错误模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ResponseBase(BaseModel):
    """响应基类"""
    success: bool = True
    message: str = "ok"


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    message: str
    error_code: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "healthy"
    version: str = "1.0.0"
    mode: str = "mock"
    timestamp: str = ""
    services: Dict[str, str] = Field(default_factory=dict)
