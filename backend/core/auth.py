"""
核心模块 - 认证
"""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """验证API Key"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    return api_key
