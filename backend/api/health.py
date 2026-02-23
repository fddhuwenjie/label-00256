"""
API路由 - 健康检查
"""
from datetime import datetime
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
