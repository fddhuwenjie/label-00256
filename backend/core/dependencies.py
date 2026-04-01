"""
依赖注入模块
提供服务的依赖注入管理，确保服务之间的解耦和可测试性
"""
from typing import Callable, TypeVar, Any
from functools import lru_cache

from services.wecom import WeComService
from services.sheet_service import SheetService
from services.local_excel import LocalExcelService


T = TypeVar('T')


class ServiceContainer:
    """
    服务容器，用于管理和注入服务实例
    
    实现了简单的依赖注入容器，支持单例模式的服务注册和解析
    """
    
    def __init__(self):
        """初始化服务容器"""
        self._services: dict[type, Any] = {}
        self._factories: dict[type, Callable[[], Any]] = {}
    
    def register(self, service_type: type[T], instance: T) -> None:
        """
        注册单例服务实例
        
        Args:
            service_type: 服务类型
            instance: 服务实例
        """
        self._services[service_type] = instance
    
    def register_factory(self, service_type: type[T], factory: Callable[[], T]) -> None:
        """
        注册服务工厂函数
        
        Args:
            service_type: 服务类型
            factory: 服务工厂函数
        """
        self._factories[service_type] = factory
    
    def get(self, service_type: type[T]) -> T:
        """
        获取服务实例
        
        Args:
            service_type: 服务类型
            
        Returns:
            服务实例
            
        Raises:
            KeyError: 服务未注册
        """
        if service_type in self._services:
            return self._services[service_type]
        
        if service_type in self._factories:
            instance = self._factories[service_type]()
            self._services[service_type] = instance
            return instance
        
        raise KeyError(f"服务未注册: {service_type.__name__}")


@lru_cache()
def get_container() -> ServiceContainer:
    """
    获取全局服务容器实例（单例）
    
    Returns:
        服务容器实例
    """
    container = ServiceContainer()
    
    wecom_service = WeComService()
    container.register(WeComService, wecom_service)
    
    sheet_service = SheetService(wecom_service=wecom_service)
    container.register(SheetService, sheet_service)
    
    local_excel_service = LocalExcelService()
    container.register(LocalExcelService, local_excel_service)
    
    return container


def get_wecom_service() -> WeComService:
    """
    获取企业微信服务实例（FastAPI 依赖注入用）
    
    Returns:
        企业微信服务实例
    """
    return get_container().get(WeComService)


def get_sheet_service() -> SheetService:
    """
    获取表格服务实例（FastAPI 依赖注入用）
    
    Returns:
        表格服务实例
    """
    return get_container().get(SheetService)


def get_local_excel_service() -> LocalExcelService:
    """
    获取本地 Excel 服务实例（FastAPI 依赖注入用）
    
    Returns:
        本地 Excel 服务实例
    """
    return get_container().get(LocalExcelService)
