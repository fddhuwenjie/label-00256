"""
API路由 - 健康检查
"""
from fastapi import APIRouter
from models.schemas import HealthResponse
from services.wecom import wecom_service

router = APIRouter(tags=["系统"])


@router.get("/health", response_model=HealthResponse, summary="健康检查")
async def health_check():
    """
    系统健康检查
    
    返回服务状态和版本信息
    """
    services = {
        "api": "healthy",
        "wecom": "configured" if wecom_service.is_configured else "mock_mode"
    }
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        services=services
    )
