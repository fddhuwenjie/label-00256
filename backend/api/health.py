"""
健康检查 API 路由
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from validators.base import HealthResponse
from services import get_wecom_service

router = APIRouter(tags=["系统"])


@router.get("/health", response_model=HealthResponse, summary="健康检查")
async def health_check(
    wecom_service=Depends(get_wecom_service),
):
    """系统健康检查

    Args:
        wecom_service: 企业微信服务实例，通过依赖注入自动获取

    Returns:
        HealthResponse: 包含服务状态和版本信息的健康检查响应
    """
    is_mock = wecom_service.is_mock_mode()

    services = {
        "api": "healthy",
        "wecom": "mock_mode" if is_mock else "configured",
    }

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        mode="mock" if is_mock else "production",
        timestamp=datetime.now().isoformat() + "Z",
        services=services,
    )
