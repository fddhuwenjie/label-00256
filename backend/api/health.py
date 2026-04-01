"""
API路由 - 健康检查
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from validators.common import HealthResponse
from services.wecom import WeComService
from services.dependencies import get_wecom_service

router = APIRouter(tags=["系统"])


@router.get("/health", response_model=HealthResponse, summary="健康检查")
async def health_check(
    wecom_service: WeComService = Depends(get_wecom_service)
):
    """
    系统健康检查
    
    Args:
        wecom_service: 企业微信服务实例（依赖注入）
        
    Returns:
        HealthResponse: 健康检查响应
    """
    is_mock = wecom_service.is_mock_mode()
    
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
