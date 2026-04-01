"""
API路由 - 健康检查
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from validators.sheets import HealthResponse
from core.dependencies import get_wecom_service
from services.wecom import WeComService

router = APIRouter(tags=["系统"])


@router.get("/health", response_model=HealthResponse, summary="健康检查")
async def health_check(
    service: WeComService = Depends(get_wecom_service)
):
    """
    系统健康检查

    Args:
        service: 企业微信服务实例

    Returns:
        健康检查响应，包含服务状态、版本、运行模式、时间戳和各服务状态
    """
    is_mock = service.is_mock_mode()
    
    services = {
        "api": "healthy",
        "wecom": "mock_mode" if is_mock else "configured"
    }
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        mode="mock" if is_mock else "production",
        timestamp=datetime.now().isoformat() + "Z",
        services=services
    )
