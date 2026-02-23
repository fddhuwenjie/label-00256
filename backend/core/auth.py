"""
核心模块 - 认证与权限控制
支持细粒度的 API Key 权限管理
"""
from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime, timedelta
from config import settings
from core.logger import logger


class Permission(str, Enum):
    """权限枚举"""
    READ = "read"           # 读取权限
    WRITE = "write"         # 写入权限
    ADMIN = "admin"         # 管理权限
    LOCAL_FILE = "local"    # 本地文件操作权限


class APIKeyInfo:
    """API Key 信息"""
    def __init__(
        self,
        key: str,
        permissions: List[Permission],
        rate_limit: int = 100,  # 每分钟请求数
        description: str = ""
    ):
        self.key = key
        self.permissions = permissions
        self.rate_limit = rate_limit
        self.description = description
        self._request_counts: Dict[str, int] = {}
        self._window_start: Optional[datetime] = None
    
    def has_permission(self, permission: Permission) -> bool:
        """检查是否有指定权限"""
        if Permission.ADMIN in self.permissions:
            return True  # 管理员拥有所有权限
        return permission in self.permissions
    
    def check_rate_limit(self) -> bool:
        """检查是否超过速率限制"""
        now = datetime.now()
        
        # 重置窗口
        if self._window_start is None or now - self._window_start > timedelta(minutes=1):
            self._window_start = now
            self._request_counts = {}
        
        # 计数
        minute_key = now.strftime("%Y%m%d%H%M")
        self._request_counts[minute_key] = self._request_counts.get(minute_key, 0) + 1
        
        return self._request_counts[minute_key] <= self.rate_limit


# API Key 配置存储
# 实际生产环境应从数据库或配置文件加载
API_KEYS_CONFIG: Dict[str, APIKeyInfo] = {
    # 默认测试 Key - 完全权限
    settings.api_key: APIKeyInfo(
        key=settings.api_key,
        permissions=[Permission.READ, Permission.WRITE, Permission.LOCAL_FILE, Permission.ADMIN],
        rate_limit=1000,
        description="默认管理员 Key"
    ),
    # 只读 Key
    "readonly-key-256": APIKeyInfo(
        key="readonly-key-256",
        permissions=[Permission.READ],
        rate_limit=100,
        description="只读访问 Key"
    ),
    # 读写 Key
    "readwrite-key-256": APIKeyInfo(
        key="readwrite-key-256",
        permissions=[Permission.READ, Permission.WRITE],
        rate_limit=60,
        description="读写访问 Key"
    ),
    # 本地文件操作 Key
    "local-file-key-256": APIKeyInfo(
        key="local-file-key-256",
        permissions=[Permission.READ, Permission.WRITE, Permission.LOCAL_FILE],
        rate_limit=30,
        description="本地文件操作 Key"
    ),
}


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key_info(api_key: str = Security(api_key_header)) -> APIKeyInfo:
    """获取 API Key 信息"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_FAILED", "message": "Missing API Key"},
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    key_info = API_KEYS_CONFIG.get(api_key)
    if not key_info:
        logger.warning(f"无效的 API Key 尝试: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_FAILED", "message": "Invalid API Key"},
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    # 检查速率限制
    if not key_info.check_rate_limit():
        logger.warning(f"API Key 超过速率限制: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": "RATE_LIMITED", "message": "Too many requests, please slow down"}
        )
    
    return key_info


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """验证API Key（兼容旧接口）"""
    key_info = await get_api_key_info(api_key)
    return key_info.key


def require_permission(permission: Permission):
    """权限检查装饰器工厂"""
    async def permission_checker(key_info: APIKeyInfo = Depends(get_api_key_info)) -> APIKeyInfo:
        if not key_info.has_permission(permission):
            logger.warning(f"权限不足: {key_info.key[:8]}... 需要 {permission.value} 权限")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "PERMISSION_DENIED",
                    "message": f"Permission denied. Required: {permission.value}"
                }
            )
        return key_info
    
    return permission_checker


# 预定义的权限检查依赖
require_read = require_permission(Permission.READ)
require_write = require_permission(Permission.WRITE)
require_admin = require_permission(Permission.ADMIN)
require_local_file = require_permission(Permission.LOCAL_FILE)


class PermissionChecker:
    """权限检查器类（用于更复杂的权限逻辑）"""
    
    def __init__(self, required_permissions: List[Permission], require_all: bool = True):
        """
        Args:
            required_permissions: 需要的权限列表
            require_all: True 表示需要所有权限，False 表示只需要其中一个
        """
        self.required_permissions = required_permissions
        self.require_all = require_all
    
    async def __call__(self, key_info: APIKeyInfo = Depends(get_api_key_info)) -> APIKeyInfo:
        if self.require_all:
            # 需要所有权限
            missing = [p for p in self.required_permissions if not key_info.has_permission(p)]
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "PERMISSION_DENIED",
                        "message": f"Missing permissions: {', '.join(p.value for p in missing)}"
                    }
                )
        else:
            # 只需要其中一个权限
            has_any = any(key_info.has_permission(p) for p in self.required_permissions)
            if not has_any:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "PERMISSION_DENIED",
                        "message": f"Need at least one of: {', '.join(p.value for p in self.required_permissions)}"
                    }
                )
        
        return key_info
